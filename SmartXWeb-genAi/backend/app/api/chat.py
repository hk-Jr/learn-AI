import json
import time
import uuid
from datetime import datetime, timezone
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.conversation import Conversation, Message
from app.models.settings import SystemSetting
from app.schemas.chat import (
    AskRequest,
    AskResponse,
    Citation,
    ConversationResponse,
    MessageResponse,
    CreateConversationRequest
)
from app.services.retrieval_engine import retrieval_engine
from app.services.llm_service import LLMService
from app.config import settings

router = APIRouter(prefix="/chat", tags=["chat"])

def _get_setting_val(db: Session, key: str, default_val: str) -> str:
    item = db.query(SystemSetting).filter(SystemSetting.key == key).first()
    return item.value if item else default_val

@router.post("/ask", response_model=AskResponse)
def ask_question(request: AskRequest, db: Session = Depends(get_db)):
    """
    Submits a user query, performs semantic retrieval from indexed documents,
    generates a grounded answer, stores conversation state, and returns citations.
    """
    start_time = time.perf_counter()

    # 1. Resolve or create conversation
    conv = None
    if request.conversation_id:
        conv = db.query(Conversation).filter(Conversation.id == request.conversation_id).first()

    if not conv:
        # Title from question snippet
        clean_title = request.question.strip()[:40] + ("..." if len(request.question) > 40 else "")
        conv = Conversation(
            id=str(uuid.uuid4()),
            title=clean_title
        )
        db.add(conv)
        db.commit()
        db.refresh(conv)

    # 2. Record user message
    user_msg = Message(
        id=str(uuid.uuid4()),
        conversation_id=conv.id,
        role="user",
        content=request.question
    )
    db.add(user_msg)
    db.commit()

    # 3. Retrieve settings
    top_k = request.top_k or int(_get_setting_val(db, "top_k", str(settings.DEFAULT_TOP_K)))
    threshold = request.similarity_threshold if request.similarity_threshold is not None else float(_get_setting_val(db, "similarity_threshold", str(settings.DEFAULT_SIMILARITY_THRESHOLD)))
    provider = request.provider or _get_setting_val(db, "llm_provider", settings.DEFAULT_LLM_PROVIDER)
    model = request.model or _get_setting_val(db, "llm_model", settings.DEFAULT_LLM_MODEL)
    gemini_key = _get_setting_val(db, "gemini_api_key", settings.GEMINI_API_KEY)
    openai_key = _get_setting_val(db, "openai_api_key", settings.OPENAI_API_KEY)
    ollama_url = _get_setting_val(db, "ollama_base_url", settings.OLLAMA_BASE_URL)

    # 4. Semantic retrieval
    citations, context_str = retrieval_engine.retrieve(
        query=request.question,
        top_k=top_k,
        similarity_threshold=threshold,
        document_ids=request.document_ids,
        gemini_key=gemini_key,
        openai_key=openai_key
    )

    # 5. Answer generation
    answer_text, model_used = LLMService.generate_answer(
        question=request.question,
        context=context_str,
        provider=provider,
        model=model,
        gemini_key=gemini_key,
        openai_key=openai_key,
        ollama_url=ollama_url
    )

    # 6. Save assistant message with serialized citations
    citations_data = [c.model_dump() for c in citations]
    assistant_msg = Message(
        id=str(uuid.uuid4()),
        conversation_id=conv.id,
        role="assistant",
        content=answer_text,
        citations_json=json.dumps(citations_data)
    )
    db.add(assistant_msg)
    conv.updated_at = datetime.now(timezone.utc)
    db.commit()

    latency = round((time.perf_counter() - start_time) * 1000, 2)

    return AskResponse(
        conversation_id=conv.id,
        user_message_id=user_msg.id,
        assistant_message_id=assistant_msg.id,
        answer=answer_text,
        citations=citations,
        latency_ms=latency,
        model_used=model_used
    )

@router.get("/conversations", response_model=List[ConversationResponse])
def get_conversations(db: Session = Depends(get_db)):
    """List all user conversations."""
    conversations = db.query(Conversation).order_by(Conversation.updated_at.desc()).all()
    results = []
    for c in conversations:
        results.append(ConversationResponse(
            id=c.id,
            title=c.title,
            created_at=c.created_at,
            updated_at=c.updated_at,
            messages=[]
        ))
    return results

@router.get("/conversations/{conversation_id}", response_model=ConversationResponse)
def get_conversation(conversation_id: str, db: Session = Depends(get_db)):
    """Get single conversation history including messages and citations."""
    conv = db.query(Conversation).filter(Conversation.id == conversation_id).first()
    if not conv:
        raise HTTPException(status_code=404, detail="Conversation not found.")

    formatted_messages = []
    for m in conv.messages:
        citations = []
        if m.citations_json:
            try:
                raw_citations = json.loads(m.citations_json)
                citations = [Citation(**c) for c in raw_citations]
            except Exception:
                citations = []
        formatted_messages.append(MessageResponse(
            id=m.id,
            conversation_id=m.conversation_id,
            role=m.role,
            content=m.content,
            citations=citations,
            created_at=m.created_at
        ))

    return ConversationResponse(
        id=conv.id,
        title=conv.title,
        created_at=conv.created_at,
        updated_at=conv.updated_at,
        messages=formatted_messages
    )

@router.post("/conversations", response_model=ConversationResponse)
def create_conversation(req: CreateConversationRequest, db: Session = Depends(get_db)):
    """Create a new conversation session."""
    conv = Conversation(
        id=str(uuid.uuid4()),
        title=req.title or "New Conversation"
    )
    db.add(conv)
    db.commit()
    db.refresh(conv)
    return ConversationResponse(
        id=conv.id,
        title=conv.title,
        created_at=conv.created_at,
        updated_at=conv.updated_at,
        messages=[]
    )

@router.delete("/conversations/{conversation_id}")
def delete_conversation(conversation_id: str, db: Session = Depends(get_db)):
    """Delete a conversation and its messages."""
    conv = db.query(Conversation).filter(Conversation.id == conversation_id).first()
    if not conv:
        raise HTTPException(status_code=404, detail="Conversation not found.")
    db.delete(conv)
    db.commit()
    return {"message": "Conversation deleted", "conversation_id": conversation_id}

@router.delete("/conversations")
def clear_all_conversations(db: Session = Depends(get_db)):
    """Clear all conversation history."""
    db.query(Message).delete()
    db.query(Conversation).delete()
    db.commit()
    return {"message": "All conversations cleared"}


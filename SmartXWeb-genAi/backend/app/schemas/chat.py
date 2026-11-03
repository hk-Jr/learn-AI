from datetime import datetime
from typing import Optional, List, Any
from pydantic import BaseModel, Field, ConfigDict

class Citation(BaseModel):
    document_id: str
    document_name: str
    page_number: int
    chunk_index: int
    similarity_score: float
    content_snippet: str
    token_count: Optional[int] = 0

class AskRequest(BaseModel):
    question: str = Field(..., min_length=1, description="User's query")
    conversation_id: Optional[str] = None
    top_k: Optional[int] = None
    similarity_threshold: Optional[float] = None
    document_ids: Optional[List[str]] = None
    provider: Optional[str] = None
    model: Optional[str] = None

class AskResponse(BaseModel):
    conversation_id: str
    user_message_id: str
    assistant_message_id: str
    answer: str
    citations: List[Citation]
    latency_ms: float
    model_used: str

class MessageResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    conversation_id: str
    role: str
    content: str
    citations: Optional[List[Citation]] = None
    created_at: datetime

class ConversationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    title: str
    created_at: datetime
    updated_at: datetime
    messages: Optional[List[MessageResponse]] = []

class CreateConversationRequest(BaseModel):
    title: Optional[str] = "New Conversation"

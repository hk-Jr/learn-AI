from typing import List, Optional
from pydantic import BaseModel, Field
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.chat import Citation
from app.services.retrieval_engine import retrieval_engine
from app.models.settings import SystemSetting
from app.config import settings

router = APIRouter(prefix="/search", tags=["search"])

class SearchQueryRequest(BaseModel):
    query: str = Field(..., min_length=1)
    top_k: int = 5
    similarity_threshold: float = 0.0
    document_ids: Optional[List[str]] = None

class SearchResponse(BaseModel):
    query: str
    total_results: int
    results: List[Citation]

@router.post("", response_model=SearchResponse)
def semantic_search(req: SearchQueryRequest, db: Session = Depends(get_db)):
    """Direct semantic similarity search across indexed document vectors."""
    gemini_key_record = db.query(SystemSetting).filter(SystemSetting.key == "gemini_api_key").first()
    gemini_key = gemini_key_record.value if gemini_key_record else settings.GEMINI_API_KEY
    openai_key_record = db.query(SystemSetting).filter(SystemSetting.key == "openai_api_key").first()
    openai_key = openai_key_record.value if openai_key_record else settings.OPENAI_API_KEY

    citations, _ = retrieval_engine.retrieve(
        query=req.query,
        top_k=req.top_k,
        similarity_threshold=req.similarity_threshold,
        document_ids=req.document_ids,
        gemini_key=gemini_key,
        openai_key=openai_key
    )

    return SearchResponse(
        query=req.query,
        total_results=len(citations),
        results=citations
    )


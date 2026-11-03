from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel
from app.schemas.document import DocumentResponse

class RecentActivityItem(BaseModel):
    id: str
    type: str  # "document_upload", "question_asked"
    title: str
    timestamp: datetime
    status: Optional[str] = None
    details: Optional[str] = None

class DashboardStatsResponse(BaseModel):
    total_documents: int
    processed_documents: int
    failed_documents: int
    processing_documents: int
    total_chunks: int
    total_questions_asked: int
    total_conversations: int
    recent_documents: List[DocumentResponse]
    recent_activity: List[RecentActivityItem]


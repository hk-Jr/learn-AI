from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.document import Document, DocumentChunk
from app.models.conversation import Conversation, Message
from app.schemas.dashboard import DashboardStatsResponse, RecentActivityItem
from app.schemas.document import DocumentResponse

router = APIRouter(prefix="/dashboard", tags=["dashboard"])

@router.get("/stats", response_model=DashboardStatsResponse)
def get_dashboard_stats(db: Session = Depends(get_db)):
    """Retrieve aggregate statistics and recent activity for the dashboard."""
    total_docs = db.query(Document).count()
    processed_docs = db.query(Document).filter(Document.status == "indexed").count()
    failed_docs = db.query(Document).filter(Document.status == "error").count()
    processing_docs = db.query(Document).filter(Document.status.in_(["pending", "processing"])).count()
    total_chunks = db.query(DocumentChunk).count()
    
    total_questions = db.query(Message).filter(Message.role == "user").count()
    total_convs = db.query(Conversation).count()

    recent_docs_records = db.query(Document).order_by(Document.uploaded_at.desc()).limit(5).all()
    recent_docs = [DocumentResponse.model_validate(d) for d in recent_docs_records]

    # Combine recent uploads and questions into activity stream
    activity_items = []

    for d in recent_docs_records:
        activity_items.append(RecentActivityItem(
            id=f"doc_{d.id}",
            type="document_upload",
            title=f"Uploaded '{d.original_name}'",
            timestamp=d.uploaded_at,
            status=d.status,
            details=f"Type: {d.file_type.upper()}, Size: {d.file_size // 1024} KB, Chunks: {d.total_chunks}"
        ))

    recent_msgs = db.query(Message).filter(Message.role == "user").order_by(Message.created_at.desc()).limit(5).all()
    for m in recent_msgs:
        snippet = m.content[:50] + ("..." if len(m.content) > 50 else "")
        activity_items.append(RecentActivityItem(
            id=f"msg_{m.id}",
            type="question_asked",
            title=f"Asked: \"{snippet}\"",
            timestamp=m.created_at,
            status="completed",
            details="Retrieved grounded knowledge"
        ))

    # Sort activity by timestamp desc
    activity_items.sort(key=lambda x: x.timestamp, reverse=True)

    return DashboardStatsResponse(
        total_documents=total_docs,
        processed_documents=processed_docs,
        failed_documents=failed_docs,
        processing_documents=processing_docs,
        total_chunks=total_chunks,
        total_questions_asked=total_questions,
        total_conversations=total_convs,
        recent_documents=recent_docs,
        recent_activity=activity_items[:10]
    )


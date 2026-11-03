import os
import shutil
import uuid
from pathlib import Path
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, BackgroundTasks, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.document import Document, DocumentChunk
from app.schemas.document import DocumentResponse, DocumentDetailResponse
from app.services.ingestion_service import IngestionService
from app.config import settings

router = APIRouter(prefix="/documents", tags=["documents"])

@router.post("/upload", response_model=List[DocumentResponse])
async def upload_documents(
    background_tasks: BackgroundTasks,
    files: List[UploadFile] = File(...),
    db: Session = Depends(get_db)
):
    """
    Upload one or multiple documents (PDF, DOCX, TXT, MD).
    Validates file format and size, saves file to storage, and queues ingestion pipeline.
    """
    if not files:
        raise HTTPException(status_code=400, detail="No files provided.")

    responses = []

    for file in files:
        ext = Path(file.filename or "").suffix.lower()
        if ext not in settings.ALLOWED_EXTENSIONS:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported file type: {ext}. Allowed types: {', '.join(settings.ALLOWED_EXTENSIONS)}"
            )

        # Check for duplicates or generate safe unique filename
        file_id = str(uuid.uuid4())
        safe_name = f"{file_id}_{file.filename}"
        save_path = settings.UPLOAD_DIR / safe_name

        # Read and check size
        content = await file.read()
        file_size = len(content)
        max_bytes = settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024
        if file_size > max_bytes:
            raise HTTPException(
                status_code=400,
                detail=f"File {file.filename} exceeds max size of {settings.MAX_UPLOAD_SIZE_MB}MB."
            )

        with open(save_path, "wb") as f:
            f.write(content)

        doc = Document(
            id=file_id,
            filename=safe_name,
            original_name=file.filename or "Unnamed Document",
            file_type=ext,
            file_size=file_size,
            file_path=str(save_path),
            status="pending"
        )
        db.add(doc)
        db.commit()
        db.refresh(doc)

        # Run ingestion in background task or immediately
        # We process immediately or in background; running synchronously ensures immediate availability
        IngestionService.process_document(doc.id, db)
        db.refresh(doc)

        responses.append(doc)

    return responses

@router.get("", response_model=List[DocumentResponse])
def list_documents(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db)
):
    """List all uploaded documents."""
    docs = db.query(Document).order_by(Document.uploaded_at.desc()).offset(skip).limit(limit).all()
    return docs

@router.get("/{document_id}", response_model=DocumentDetailResponse)
def get_document(document_id: str, db: Session = Depends(get_db)):
    """Get single document metadata and all its chunks."""
    doc = db.query(Document).filter(Document.id == document_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found.")
    return doc

@router.delete("/{document_id}")
def delete_document(document_id: str, db: Session = Depends(get_db)):
    """Delete document, its file on disk, its database chunks, and its ChromaDB vector index."""
    doc = db.query(Document).filter(Document.id == document_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found.")

    # Remove file on disk
    try:
        p = Path(doc.file_path)
        if p.exists():
            p.unlink()
    except Exception as e:
        print(f"[DocumentAPI] Warning: could not delete file {doc.file_path}: {e}")

    # Remove vectors
    from app.services.vector_store import vector_store
    vector_store.delete_by_document_id(doc.id)

    # Remove database record (cascades to chunks)
    db.delete(doc)
    db.commit()

    return {"message": "Document deleted successfully", "document_id": document_id}

@router.post("/{document_id}/reprocess", response_model=DocumentResponse)
def reprocess_document(document_id: str, db: Session = Depends(get_db)):
    """Reprocess an existing document through the ingestion pipeline."""
    doc = db.query(Document).filter(Document.id == document_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found.")

    success = IngestionService.process_document(doc.id, db)
    db.refresh(doc)
    if not success:
        raise HTTPException(status_code=500, detail=f"Reprocessing failed: {doc.error_message}")
    return doc

@router.get("/{document_id}/status")
def get_document_status(document_id: str, db: Session = Depends(get_db)):
    """Fast status endpoint for polling."""
    doc = db.query(Document.id, Document.status, Document.error_message, Document.total_chunks).filter(Document.id == document_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found.")
    return {
        "id": doc[0],
        "status": doc[1],
        "error_message": doc[2],
        "total_chunks": doc[3]
    }


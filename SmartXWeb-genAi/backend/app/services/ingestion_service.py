import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional
from sqlalchemy.orm import Session
from app.models.document import Document, DocumentChunk
from app.services.document_parser import DocumentParser
from app.services.text_chunker import TextChunker
from app.services.embedding_service import EmbeddingService
from app.services.vector_store import vector_store
from app.config import settings

class IngestionService:
    @classmethod
    def process_document(
        cls,
        document_id: str,
        db: Session,
        chunk_size: Optional[int] = None,
        chunk_overlap: Optional[int] = None,
        gemini_key: Optional[str] = None,
        openai_key: Optional[str] = None
    ) -> bool:
        """
        Executes the full automated ingestion pipeline:
        1. Fetch document record
        2. Parse file content
        3. Chunk text into semantically cohesive pieces
        4. Generate embeddings
        5. Store in vector database
        6. Store chunk records in relational database
        7. Update document status to 'indexed'
        """
        doc = db.query(Document).filter(Document.id == document_id).first()
        if not doc:
            return False

        doc.status = "processing"
        doc.error_message = None
        db.commit()

        file_path = Path(doc.file_path)
        if not file_path.exists():
            doc.status = "error"
            doc.error_message = f"File not found on disk: {file_path}"
            db.commit()
            return False

        try:
            # 1. Parse text
            pages, total_pages, total_chars = DocumentParser.parse_file(file_path, doc.file_type)
            doc.total_pages = total_pages
            doc.total_characters = total_chars

            if total_chars == 0:
                doc.status = "error"
                doc.error_message = "No readable text extracted from document."
                db.commit()
                return False

            # 2. Chunk text
            c_size = chunk_size or settings.DEFAULT_CHUNK_SIZE
            c_overlap = chunk_overlap or settings.DEFAULT_CHUNK_OVERLAP
            chunker = TextChunker(chunk_size=c_size, chunk_overlap=c_overlap)
            chunks = chunker.chunk_pages(pages)

            if not chunks:
                doc.status = "error"
                doc.error_message = "Failed to produce text chunks."
                db.commit()
                return False

            doc.total_chunks = len(chunks)

            # 3. Clean any existing chunks for this doc in DB and vector store
            db.query(DocumentChunk).filter(DocumentChunk.document_id == doc.id).delete()
            vector_store.delete_by_document_id(doc.id)

            # 4. Generate embeddings
            embed_service = EmbeddingService(
                provider=settings.DEFAULT_EMBEDDING_PROVIDER,
                model=settings.DEFAULT_EMBEDDING_MODEL
            )
            contents = [c.content for c in chunks]
            embeddings = embed_service.embed_texts(
                contents,
                gemini_key=gemini_key,
                openai_key=openai_key
            )

            # 5. Store in ChromaDB
            vector_ids = [f"{doc.id}_{c.chunk_index}" for c in chunks]
            metadatas = [
                {
                    "document_id": doc.id,
                    "document_name": doc.original_name,
                    "page_number": c.page_number,
                    "chunk_index": c.chunk_index,
                    "token_count": c.token_count
                }
                for c in chunks
            ]
            vector_store.add_chunks(
                ids=vector_ids,
                documents=contents,
                embeddings=embeddings,
                metadatas=metadatas
            )

            # 6. Store in SQLite
            for c, v_id in zip(chunks, vector_ids):
                db_chunk = DocumentChunk(
                    document_id=doc.id,
                    chunk_index=c.chunk_index,
                    page_number=c.page_number,
                    content=c.content,
                    token_count=c.token_count,
                    vector_id=v_id
                )
                db.add(db_chunk)

            # 7. Complete processing
            doc.status = "indexed"
            doc.processed_at = datetime.now(timezone.utc)
            db.commit()
            return True

        except Exception as e:
            db.rollback()
            doc.status = "error"
            doc.error_message = str(e)
            db.commit()
            print(f"[IngestionService] Error processing document {doc.id}: {e}")
            return False


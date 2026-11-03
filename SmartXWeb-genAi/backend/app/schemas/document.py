from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, ConfigDict

class DocumentChunkResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    chunk_index: int
    page_number: int
    content: str
    token_count: int
    vector_id: str

class DocumentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    filename: str
    original_name: str
    file_type: str
    file_size: int
    status: str
    error_message: Optional[str] = None
    total_pages: int
    total_chunks: int
    total_characters: int
    uploaded_at: datetime
    processed_at: Optional[datetime] = None

class DocumentDetailResponse(DocumentResponse):
    chunks: List[DocumentChunkResponse] = []

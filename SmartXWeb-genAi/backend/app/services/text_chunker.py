import re
from typing import List, Dict, Any
from app.services.document_parser import ExtractedPage

class ChunkItem:
    def __init__(self, chunk_index: int, page_number: int, content: str, token_count: int):
        self.chunk_index = chunk_index
        self.page_number = page_number
        self.content = content
        self.token_count = token_count

    def to_dict(self) -> Dict[str, Any]:
        return {
            "chunk_index": self.chunk_index,
            "page_number": self.page_number,
            "content": self.content,
            "token_count": self.token_count
        }

class TextChunker:
    def __init__(self, chunk_size: int = 500, chunk_overlap: int = 50):
        self.chunk_size = max(100, chunk_size)
        self.chunk_overlap = min(chunk_overlap, self.chunk_size // 2)

    def _split_into_units(self, text: str) -> List[str]:
        """Split text cleanly into paragraph units or sentence units."""
        # Split on paragraphs first
        paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
        units = []
        for para in paragraphs:
            if len(para) <= self.chunk_size:
                units.append(para)
            else:
                # Split large paragraph into sentences
                sentences = re.split(r'(?<=[.!?])\s+', para)
                current_sent = ""
                for sent in sentences:
                    sent = sent.strip()
                    if not sent:
                        continue
                    if len(current_sent) + len(sent) + 1 <= self.chunk_size:
                        current_sent = f"{current_sent} {sent}".strip()
                    else:
                        if current_sent:
                            units.append(current_sent)
                        # If a single sentence exceeds chunk_size, split by words
                        if len(sent) > self.chunk_size:
                            words = sent.split(" ")
                            sub_w = ""
                            for w in words:
                                if len(sub_w) + len(w) + 1 <= self.chunk_size:
                                    sub_w = f"{sub_w} {w}".strip()
                                else:
                                    if sub_w:
                                        units.append(sub_w)
                                    sub_w = w
                            if sub_w:
                                units.append(sub_w)
                            current_sent = ""
                        else:
                            current_sent = sent
                if current_sent:
                    units.append(current_sent)
        return units

    def chunk_pages(self, pages: List[ExtractedPage]) -> List[ChunkItem]:
        """
        Chunks pages preserving page numbers, enforcing chunk_size and chunk_overlap.
        """
        chunks: List[ChunkItem] = []
        global_chunk_idx = 0

        for page in pages:
            page_text = page.text.strip()
            if not page_text:
                continue

            units = self._split_into_units(page_text)
            if not units:
                continue

            current_chunk = ""
            for unit in units:
                if not current_chunk:
                    current_chunk = unit
                elif len(current_chunk) + len(unit) + 2 <= self.chunk_size:
                    current_chunk = f"{current_chunk}\n\n{unit}"
                else:
                    # Current chunk is full, record it
                    tokens = max(1, len(current_chunk) // 4)
                    chunks.append(ChunkItem(
                        chunk_index=global_chunk_idx,
                        page_number=page.page_number,
                        content=current_chunk,
                        token_count=tokens
                    ))
                    global_chunk_idx += 1

                    # Apply overlap: take the tail of the current chunk
                    if self.chunk_overlap > 0 and len(current_chunk) > self.chunk_overlap:
                        overlap_text = current_chunk[-self.chunk_overlap:]
                        # Try not to slice a word in half
                        space_idx = overlap_text.find(" ")
                        if space_idx != -1:
                            overlap_text = overlap_text[space_idx + 1:]
                        current_chunk = f"{overlap_text}\n{unit}".strip()
                    else:
                        current_chunk = unit

            if current_chunk.strip():
                tokens = max(1, len(current_chunk) // 4)
                chunks.append(ChunkItem(
                    chunk_index=global_chunk_idx,
                    page_number=page.page_number,
                    content=current_chunk.strip(),
                    token_count=tokens
                ))
                global_chunk_idx += 1

        return chunks


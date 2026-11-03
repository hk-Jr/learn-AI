import os
import re
from pathlib import Path
from typing import List, Dict, Any, Tuple
import pymupdf  # PyMuPDF
import docx

class ExtractedPage:
    def __init__(self, page_number: int, text: str):
        self.page_number = page_number
        self.text = text

class DocumentParser:
    @staticmethod
    def clean_text(text: str) -> str:
        """Clean and normalize extracted text."""
        if not text:
            return ""
        # Normalize whitespace and line breaks
        text = re.sub(r'\r\n|\r', '\n', text)
        text = re.sub(r'[ \t]+', ' ', text)
        text = re.sub(r'\n{3,}', '\n\n', text)
        return text.strip()

    @classmethod
    def parse_pdf(cls, file_path: Path) -> List[ExtractedPage]:
        """Extract text per page from PDF using PyMuPDF."""
        pages = []
        doc = pymupdf.open(str(file_path))
        try:
            for page_idx in range(len(doc)):
                page = doc[page_idx]
                text = page.get_text("text") or ""
                cleaned = cls.clean_text(text)
                # Keep page even if text is empty to maintain correct page indexing
                pages.append(ExtractedPage(page_number=page_idx + 1, text=cleaned))
        finally:
            doc.close()
        return pages

    @classmethod
    def parse_docx(cls, file_path: Path) -> List[ExtractedPage]:
        """Extract text from Word DOCX document."""
        doc = docx.Document(str(file_path))
        full_text_parts = []
        
        # Paragraphs
        for para in doc.paragraphs:
            if para.text.strip():
                full_text_parts.append(para.text.strip())
                
        # Tables
        for table in doc.tables:
            for row in table.rows:
                row_text = " | ".join(cell.text.strip() for cell in row.cells if cell.text.strip())
                if row_text:
                    full_text_parts.append(row_text)
                    
        combined_text = "\n\n".join(full_text_parts)
        cleaned = cls.clean_text(combined_text)
        
        # DOCX files do not have explicit fixed page breaks easily; paginate roughly by 2500 chars if long
        if len(cleaned) <= 3000:
            return [ExtractedPage(page_number=1, text=cleaned)]
        
        # Synthetic pagination for large docs
        pages = []
        page_size = 2500
        for i in range(0, len(cleaned), page_size):
            page_text = cleaned[i:i + page_size]
            pages.append(ExtractedPage(page_number=len(pages) + 1, text=page_text))
        return pages

    @classmethod
    def parse_plain_text(cls, file_path: Path) -> List[ExtractedPage]:
        """Extract text from TXT or Markdown files with fallback encodings."""
        raw_text = None
        for encoding in ["utf-8", "utf-8-sig", "latin-1", "cp1252"]:
            try:
                with open(file_path, "r", encoding=encoding) as f:
                    raw_text = f.read()
                break
            except (UnicodeDecodeError, LookupError):
                continue
                
        if raw_text is None:
            # Fallback to binary with error replace
            with open(file_path, "rb") as f:
                raw_text = f.read().decode("utf-8", errors="replace")
                
        cleaned = cls.clean_text(raw_text)
        
        if len(cleaned) <= 3000:
            return [ExtractedPage(page_number=1, text=cleaned)]
        
        pages = []
        page_size = 2500
        for i in range(0, len(cleaned), page_size):
            pages.append(ExtractedPage(page_number=len(pages) + 1, text=cleaned[i:i + page_size]))
        return pages

    @classmethod
    def parse_file(cls, file_path: Path, file_type: str) -> Tuple[List[ExtractedPage], int, int]:
        """
        Parses document according to type.
        Returns: (List[ExtractedPage], total_pages, total_characters)
        """
        ext = file_type.lower()
        if not ext.startswith("."):
            ext = f".{ext}"

        if ext == ".pdf":
            pages = cls.parse_pdf(file_path)
        elif ext in [".docx", ".doc"]:
            pages = cls.parse_docx(file_path)
        elif ext in [".txt", ".md", ".markdown", ".csv", ".json"]:
            pages = cls.parse_plain_text(file_path)
        else:
            # Try text parser by default
            pages = cls.parse_plain_text(file_path)

        total_pages = len(pages)
        total_chars = sum(len(p.text) for p in pages)
        return pages, total_pages, total_chars


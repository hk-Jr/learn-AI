from typing import List, Dict, Any, Optional, Tuple
from app.services.embedding_service import EmbeddingService
from app.services.vector_store import vector_store
from app.schemas.chat import Citation
from app.config import settings

class RetrievalEngine:
    def __init__(self, embedding_service: Optional[EmbeddingService] = None):
        self.embedding_service = embedding_service or EmbeddingService()

    def retrieve(
        self,
        query: str,
        top_k: int = 4,
        similarity_threshold: float = 0.3,
        document_ids: Optional[List[str]] = None,
        gemini_key: Optional[str] = None,
        openai_key: Optional[str] = None
    ) -> Tuple[List[Citation], str]:
        """
        Retrieves relevant document chunks and constructs grounded context string.
        Returns: (List[Citation], context_str)
        """
        # 1. Generate query embedding
        query_vec = self.embedding_service.embed_query(
            query,
            gemini_key=gemini_key,
            openai_key=openai_key
        )

        # 2. Vector search in ChromaDB
        hits = vector_store.query(
            query_embedding=query_vec,
            top_k=top_k * 2 if similarity_threshold > 0 else top_k, # Fetch surplus for filtering
            document_ids=document_ids
        )

        # 3. Filter by threshold and take top_k
        filtered_hits = [
            h for h in hits if h["similarity_score"] >= similarity_threshold
        ][:top_k]

        citations: List[Citation] = []
        context_blocks: List[str] = []

        for idx, hit in enumerate(filtered_hits, 1):
            meta = hit.get("metadata", {})
            doc_id = meta.get("document_id", "unknown")
            doc_name = meta.get("document_name", "Document")
            page_num = int(meta.get("page_number", 1))
            chunk_idx = int(meta.get("chunk_index", 0))
            score = hit["similarity_score"]
            content = hit.get("content", "").strip()

            snippet = content[:300] + ("..." if len(content) > 300 else "")
            tokens = max(1, len(content) // 4)

            citation = Citation(
                document_id=doc_id,
                document_name=doc_name,
                page_number=page_num,
                chunk_index=chunk_idx,
                similarity_score=score,
                content_snippet=snippet,
                token_count=tokens
            )
            citations.append(citation)

            # Block format for LLM context
            context_blocks.append(
                f"[Source {idx}: Document '{doc_name}', Page {page_num}, Chunk #{chunk_idx}]\n{content}"
            )

        context_str = "\n\n---\n\n".join(context_blocks) if context_blocks else ""
        return citations, context_str

# Singleton
retrieval_engine = RetrievalEngine()


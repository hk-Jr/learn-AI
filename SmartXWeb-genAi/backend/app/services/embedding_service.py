import os
import math
import hashlib
from typing import List, Optional
import httpx
from app.config import settings

class EmbeddingService:
    def __init__(self, provider: str = "chroma_default", model: str = "text-embedding-004"):
        self.provider = provider
        self.model = model

    @staticmethod
    def _deterministic_local_embedding(text: str, dim: int = 384) -> List[float]:
        """
        High-dimensional deterministic dense vector for zero-dependency local embedding.
        Uses multi-hash n-gram projection with L2 normalization.
        Ensures consistent, instant, offline-capable similarity matching.
        """
        vec = [0.0] * dim
        words = text.lower().split()
        if not words:
            return vec

        # Bag of words and character n-grams
        tokens = words + [text[i:i+3].lower() for i in range(max(0, len(text) - 2))]
        for token in tokens:
            h = int(hashlib.md5(token.encode('utf-8')).hexdigest(), 16)
            idx = h % dim
            sign = 1.0 if ((h >> 1) & 1) else -1.0
            vec[idx] += sign

        # L2 normalize
        norm = math.sqrt(sum(v * v for v in vec))
        if norm > 0:
            vec = [v / norm for v in vec]
        return vec

    def embed_texts(self, texts: List[str], gemini_key: Optional[str] = None, openai_key: Optional[str] = None) -> List[List[float]]:
        """Generate embeddings for a list of strings."""
        if not texts:
            return []

        # Check for Gemini
        gemini_api_key = gemini_key or settings.GEMINI_API_KEY
        if self.provider == "gemini" and gemini_api_key:
            try:
                from google import genai
                client = genai.Client(api_key=gemini_api_key)
                embeddings = []
                for text in texts:
                    res = client.models.embed_content(
                        model=self.model or "text-embedding-004",
                        contents=text
                    )
                    embeddings.append(res.embedding.values)
                return embeddings
            except Exception as e:
                print(f"[EmbeddingService] Gemini embedding error, using local fallback: {e}")

        # Check for OpenAI
        openai_api_key = openai_key or settings.OPENAI_API_KEY
        if self.provider == "openai" and openai_api_key:
            try:
                from openai import OpenAI
                client = OpenAI(api_key=openai_api_key)
                response = client.embeddings.create(
                    input=texts,
                    model=self.model or "text-embedding-3-small"
                )
                return [item.embedding for item in response.data]
            except Exception as e:
                print(f"[EmbeddingService] OpenAI embedding error, using local fallback: {e}")

        # Try ChromaDB default embedding function if available
        try:
            import chromadb.utils.embedding_functions as ef
            default_ef = ef.DefaultEmbeddingFunction()
            return default_ef(texts)
        except Exception as e:
            # Fallback to deterministic dense projection
            return [self._deterministic_local_embedding(t) for t in texts]

    def embed_query(self, query: str, gemini_key: Optional[str] = None, openai_key: Optional[str] = None) -> List[float]:
        """Generate embedding for a single query."""
        results = self.embed_texts([query], gemini_key=gemini_key, openai_key=openai_key)
        return results[0] if results else [0.0] * 384


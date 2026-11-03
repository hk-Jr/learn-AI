from typing import List, Dict, Any, Optional
import chromadb
from chromadb.config import Settings as ChromaSettings
from app.config import settings

class VectorStore:
    def __init__(self, collection_name: str = "knowledge_base"):
        self.collection_name = collection_name
        self.client = chromadb.PersistentClient(
            path=str(settings.CHROMA_DIR),
            settings=ChromaSettings(anonymized_telemetry=False)
        )
        self.collection = self.client.get_or_create_collection(
            name=self.collection_name,
            metadata={"hnsw:space": "cosine"}
        )

    def add_chunks(
        self,
        ids: List[str],
        documents: List[str],
        embeddings: List[List[float]],
        metadatas: List[Dict[str, Any]]
    ) -> None:
        """Add or update vector chunks in ChromaDB."""
        if not ids:
            return

        # ChromaDB requires metadata values to be str, int, float, or bool
        clean_metadatas = []
        for meta in metadatas:
            clean_meta = {}
            for k, v in meta.items():
                if v is None:
                    continue
                if isinstance(v, (str, int, float, bool)):
                    clean_meta[k] = v
                else:
                    clean_meta[k] = str(v)
            clean_metadatas.append(clean_meta)

        self.collection.upsert(
            ids=ids,
            documents=documents,
            embeddings=embeddings,
            metadatas=clean_metadatas
        )

    def query(
        self,
        query_embedding: List[float],
        top_k: int = 4,
        document_ids: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """
        Query nearest neighbors with optional document ID filter.
        Returns a formatted list of matches with similarity scores.
        """
        where_filter = None
        if document_ids:
            if len(document_ids) == 1:
                where_filter = {"document_id": document_ids[0]}
            else:
                where_filter = {"document_id": {"$in": document_ids}}

        try:
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=top_k,
                where=where_filter,
                include=["documents", "metadatas", "distances"]
            )
        except Exception as e:
            print(f"[VectorStore] Query error: {e}")
            return []

        hits = []
        if not results or not results["ids"] or not results["ids"][0]:
            return hits

        ids = results["ids"][0]
        docs = results["documents"][0] if results.get("documents") else []
        metas = results["metadatas"][0] if results.get("metadatas") else []
        distances = results["distances"][0] if results.get("distances") else []

        for i, vector_id in enumerate(ids):
            # For cosine distance: distance = 1 - cosine_similarity
            # Therefore cosine_similarity = max(0.0, 1.0 - dist)
            dist = distances[i] if i < len(distances) else 1.0
            similarity = max(0.0, min(1.0, 1.0 - dist))

            hits.append({
                "vector_id": vector_id,
                "content": docs[i] if i < len(docs) else "",
                "metadata": metas[i] if i < len(metas) else {},
                "similarity_score": round(similarity, 4),
                "distance": round(dist, 4)
            })

        return hits

    def delete_by_document_id(self, document_id: str) -> None:
        """Remove all chunks associated with a specific document."""
        try:
            self.collection.delete(where={"document_id": document_id})
        except Exception as e:
            print(f"[VectorStore] Delete document chunks error: {e}")

    def count(self) -> int:
        """Count total vectors in collection."""
        try:
            return self.collection.count()
        except Exception:
            return 0

# Global singleton
vector_store = VectorStore()

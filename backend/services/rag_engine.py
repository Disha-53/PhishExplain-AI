from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

import faiss
from sentence_transformers import SentenceTransformer

from backend.config import KNOWLEDGE_DIR, RAG_EMBEDDING_MODEL, RAG_TOP_K, VECTOR_DB_DIR


class RAGEngine:
    def __init__(self, knowledge_dir: str | None = None, vector_db_dir: str | None = None):
        self.knowledge_dir = Path(knowledge_dir or KNOWLEDGE_DIR)
        self.vector_db_dir = Path(vector_db_dir or VECTOR_DB_DIR)
        self.index = None
        self.chunks: list[dict[str, Any]] = []
        self.embedder = None
        self.status = "unavailable"
        self._load_index()

    def _load_index(self) -> None:
        index_path = self.vector_db_dir / "knowledge.faiss"
        metadata_path = self.vector_db_dir / "knowledge_chunks.json"
        model_path = self.vector_db_dir / "knowledge_embedding_model.json"
        if not index_path.exists() or not metadata_path.exists():
            return
        try:
            self.index = faiss.read_index(str(index_path))
            self.chunks = json.loads(metadata_path.read_text(encoding="utf-8"))
            configured_model = RAG_EMBEDDING_MODEL
            if model_path.exists():
                configured_model = json.loads(model_path.read_text(encoding="utf-8")).get("model", configured_model)
            self.embedder = SentenceTransformer(configured_model)
            self.status = "ready"
        except Exception:
            self.index = None
            self.chunks = []
            self.embedder = None
            self.status = "unavailable"

    def retrieve(self, query: str) -> dict[str, Any]:
        if self.status != "ready" or not (query or "").strip():
            return {"source": "fallback (embedding index unavailable)", "status": self.status, "results": []}
        vector = self.embedder.encode([query], normalize_embeddings=True)
        scores, indices = self.index.search(vector, RAG_TOP_K)
        results = []
        for score, index in zip(scores[0], indices[0]):
            if index < 0 or index >= len(self.chunks):
                continue
            item = dict(self.chunks[index])
            item["similarity"] = round(float(score), 6)
            results.append(item)
        return {"source": "embedding index", "status": self.status, "results": results}

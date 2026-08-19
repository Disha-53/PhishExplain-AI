"""Build the persistent FAISS index used by the backend RAG engine."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

import faiss
import numpy as np
from sentence_transformers import SentenceTransformer

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from backend.config import KNOWLEDGE_DIR, RAG_EMBEDDING_MODEL, VECTOR_DB_DIR


def chunks_for_document(content: str, document_id: str, title: str, chunk_size: int, overlap: int) -> list[dict]:
    words = content.split()
    results = []
    step = max(1, chunk_size - overlap)
    for start in range(0, len(words), step):
        text = " ".join(words[start : start + chunk_size]).strip()
        if not text:
            continue
        chunk_id = hashlib.sha256(f"{document_id}:{start}:{text}".encode()).hexdigest()[:16]
        results.append(
            {
                "chunk_id": chunk_id,
                "document_id": document_id,
                "title": title,
                "source": "repository-local knowledge document",
                "topic": document_id,
                "source_url": None,
                "last_updated": None,
                "text": text,
            }
        )
    return results


def build(knowledge_dir: Path, output_dir: Path, chunk_size: int = 180, overlap: int = 30) -> int:
    chunks = []
    for path in sorted(knowledge_dir.glob("*.md")):
        content = path.read_text(encoding="utf-8").strip()
        chunks.extend(chunks_for_document(content, path.stem, path.stem.replace("_", " ").title(), chunk_size, overlap))
    if not chunks:
        raise ValueError(f"No Markdown knowledge documents found under {knowledge_dir}")
    embedder = SentenceTransformer(RAG_EMBEDDING_MODEL)
    vectors = embedder.encode([item["text"] for item in chunks], normalize_embeddings=True, show_progress_bar=True)
    index = faiss.IndexFlatIP(vectors.shape[1])
    index.add(np.asarray(vectors, dtype="float32"))
    output_dir.mkdir(parents=True, exist_ok=True)
    faiss.write_index(index, str(output_dir / "knowledge.faiss"))
    (output_dir / "knowledge_chunks.json").write_text(json.dumps(chunks, indent=2), encoding="utf-8")
    (output_dir / "knowledge_embedding_model.json").write_text(
        json.dumps({"model": RAG_EMBEDDING_MODEL, "chunk_size": chunk_size, "overlap": overlap}, indent=2),
        encoding="utf-8",
    )
    print(f"Indexed {len(chunks)} chunks in {output_dir}")
    return len(chunks)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--knowledge-dir", type=Path, default=KNOWLEDGE_DIR)
    parser.add_argument("--output-dir", type=Path, default=VECTOR_DB_DIR)
    parser.add_argument("--chunk-size", type=int, default=180)
    parser.add_argument("--overlap", type=int, default=30)
    args = parser.parse_args()
    build(args.knowledge_dir, args.output_dir, args.chunk_size, args.overlap)


if __name__ == "__main__":
    main()
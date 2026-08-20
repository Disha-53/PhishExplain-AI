from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv


PROJECT_ROOT = Path(__file__).resolve().parents[1]
load_dotenv(PROJECT_ROOT / ".env")


def _path_from_env(name: str, default: Path) -> Path:
    value = os.getenv(name, "").strip()
    path = Path(value) if value else default
    return path if path.is_absolute() else PROJECT_ROOT / path


MODEL_DIR = _path_from_env("MODEL_DIR", PROJECT_ROOT / "models")
KNOWLEDGE_DIR = _path_from_env("KNOWLEDGE_DIR", PROJECT_ROOT / "knowledge")
VECTOR_DB_DIR = _path_from_env("VECTOR_DB_DIR", PROJECT_ROOT / "data" / "vector_db")

ENVIRONMENT = os.getenv("ENVIRONMENT", os.getenv("MODEL_ENV", "development"))
API_HOST = os.getenv("API_HOST", "127.0.0.1")
API_PORT = int(os.getenv("API_PORT", os.getenv("PORT", "8000")))
RAG_TOP_K = int(os.getenv("RAG_TOP_K", "3"))
RAG_EMBEDDING_MODEL = os.getenv(
    "RAG_EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2"
)


def cors_origins() -> list[str]:
    configured = os.getenv("CORS_ORIGINS", "")
    if configured.strip():
        return [origin.strip() for origin in configured.split(",") if origin.strip()]
    if ENVIRONMENT == "development":
        return [
            "null",
            "http://localhost:8000",
            "http://127.0.0.1:8000",
            "http://localhost:5500",
            "http://127.0.0.1:5500",
        ]
    return []
"""Report dependency, artifact, path, and backend import readiness."""

from __future__ import annotations

import importlib
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from backend.config import KNOWLEDGE_DIR, MODEL_DIR, VECTOR_DB_DIR


MODULES = ("fastapi", "uvicorn", "pandas", "numpy", "sklearn", "joblib", "sentence_transformers", "faiss", "streamlit", "requests")


def main() -> int:
    failures = []
    for module in MODULES:
        try:
            importlib.import_module(module)
            print(f"OK dependency: {module}")
        except Exception as error:
            failures.append(f"{module}: {error}")
            print(f"FAIL dependency: {module}: {error}")
    for path, description in ((MODEL_DIR, "model directory"), (KNOWLEDGE_DIR, "knowledge directory"), (VECTOR_DB_DIR, "vector directory")):
        print(f"{'OK' if path.exists() else 'WARN'} {description}: {path}")
    try:
        from backend.main import app
        print(f"OK backend import: {app.title}")
    except Exception as error:
        failures.append(f"backend import: {error}")
        print(f"FAIL backend import: {error}")
    if failures:
        print("\nSetup verification failed:")
        print("\n".join(f"- {failure}" for failure in failures))
        return 1
    print("\nCore setup verification passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
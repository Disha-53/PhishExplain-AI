from __future__ import annotations

import re


def safe_text(value: str | None, fallback: str = "") -> str:
    if value is None:
        return fallback
    return re.sub(r"\s+", " ", str(value)).strip()[:5000] or fallback


def redact_for_logging(value: str | None) -> str:
    if not value:
        return ""
    return re.sub(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}", "[REDACTED_EMAIL]", value)[:200]

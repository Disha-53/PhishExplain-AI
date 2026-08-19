"""Normalize locally downloaded email corpora into text,label,source CSV rows."""

from __future__ import annotations

import argparse
import csv
import hashlib
import mailbox
import re
import sys
from email.message import Message
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from backend.config import PROJECT_ROOT


LABEL_MAP = {
    "ham": 0,
    "legitimate": 0,
    "genuine": 0,
    "safe": 0,
    "spam": 1,
    "phishing": 1,
    "malicious": 1,
}


def clean_text(value: object) -> str:
    return re.sub(r"\s+", " ", str(value or "")).strip()


def label_value(value: object) -> int | None:
    normalized = clean_text(value).lower()
    if normalized in LABEL_MAP:
        return LABEL_MAP[normalized]
    if normalized in {"0", "1"}:
        return int(normalized)
    return None


def add_row(rows: list[dict[str, object]], text: object, label: object, source: str) -> None:
    cleaned = clean_text(text)
    mapped = label_value(label)
    if cleaned and mapped is not None:
        rows.append({"text": cleaned, "label": mapped, "source": source})


def load_tabular(path: Path, source: str) -> list[dict[str, object]]:
    frame = pd.read_csv(path)
    lowered = {str(column).lower(): column for column in frame.columns}
    text_column = next((lowered[name] for name in ("text", "body", "message", "content") if name in lowered), None)
    label_column = next((lowered[name] for name in ("label", "class", "category", "target") if name in lowered), None)
    if text_column is None or label_column is None:
        raise ValueError(f"{path} needs a text/body/message/content and label/class/category/target column")
    rows: list[dict[str, object]] = []
    for _, row in frame.iterrows():
        add_row(rows, row[text_column], row[label_column], source)
    return rows


def message_text(message: Message) -> str:
    parts = []
    if message.get("Subject"):
        parts.append(message.get("Subject", ""))
    if message.is_multipart():
        for part in message.walk():
            if part.get_content_type() == "text/plain":
                parts.append(part.get_payload(decode=True) or b"")
    else:
        parts.append(message.get_payload(decode=True) or message.get_payload())
    return clean_text(" ".join(part.decode(errors="replace") if isinstance(part, bytes) else str(part) for part in parts))


def load_nazario(path: Path) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for message in mailbox.mbox(path):
        add_row(rows, message_text(message), "phishing", "nazario")
    return rows


def process(input_dir: Path, output_path: Path) -> int:
    rows: list[dict[str, object]] = []
    for path in sorted(input_dir.rglob("*")):
        if not path.is_file():
            continue
        source = path.parent.name
        if path.suffix.lower() in {".csv", ".tsv"}:
            rows.extend(load_tabular(path, source))
        elif path.suffix.lower() == ".mbox" or path.name.startswith("phishing"):
            rows.extend(load_nazario(path))

    frame = pd.DataFrame(rows, columns=["text", "label", "source"])
    if frame.empty:
        raise ValueError(f"No supported labelled files found under {input_dir}")
    frame["content_hash"] = frame["text"].map(lambda text: hashlib.sha256(text.encode()).hexdigest())
    frame = frame.drop_duplicates(subset=["content_hash"]).drop(columns=["content_hash"])
    output_path.parent.mkdir(parents=True, exist_ok=True)
    frame.to_csv(output_path, index=False, quoting=csv.QUOTE_MINIMAL)
    print(f"Wrote {len(frame)} unique rows to {output_path}")
    return len(frame)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input-dir", type=Path, default=PROJECT_ROOT / "data" / "raw")
    parser.add_argument("--output", type=Path, default=PROJECT_ROOT / "data" / "processed" / "text" / "messages.csv")
    args = parser.parse_args()
    process(args.input_dir, args.output)


if __name__ == "__main__":
    main()
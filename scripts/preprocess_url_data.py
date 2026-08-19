"""Extract only inference-reproducible URL features from PhiUSIIL CSV data."""

from __future__ import annotations

import argparse
import sys
import zipfile
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from backend.config import PROJECT_ROOT
from backend.services.url_features import FEATURE_NAMES, extract_url_features


def locate_csv(input_path: Path) -> Path:
    if input_path.suffix.lower() == ".zip":
        extract_dir = input_path.parent / input_path.stem
        extract_dir.mkdir(exist_ok=True)
        with zipfile.ZipFile(input_path) as archive:
            archive.extractall(extract_dir)
        candidates = list(extract_dir.rglob("*.csv"))
        if not candidates:
            raise ValueError(f"No CSV found in {input_path}")
        return candidates[0]
    return input_path


def preprocess(input_path: Path, output_path: Path) -> int:
    csv_path = locate_csv(input_path)
    frame = pd.read_csv(csv_path)
    columns = {str(column).lower(): column for column in frame.columns}
    url_column = columns.get("url")
    label_column = columns.get("label")
    if url_column is None or label_column is None:
        raise ValueError(f"{csv_path} must contain URL and Label columns; found {list(frame.columns)}")
    output = []
    for _, row in frame[[url_column, label_column]].dropna().drop_duplicates().iterrows():
        # PhiUSIIL publishes 1=legitimate and 0=phishing; deployable labels use 0=safe, 1=phishing.
        source_label = int(row[label_column])
        if source_label not in {0, 1}:
            raise ValueError(f"Unexpected PhiUSIIL label: {source_label}")
        features = extract_url_features(str(row[url_column]))
        output.append({"url": str(row[url_column]), "label": 1 - source_label, "source": "phiusiil", **features})
    result = pd.DataFrame(output, columns=["url", "label", "source", *FEATURE_NAMES])
    output_path.parent.mkdir(parents=True, exist_ok=True)
    result.to_csv(output_path, index=False)
    print(f"Wrote {len(result)} URL rows to {output_path}")
    return len(result)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, default=PROJECT_ROOT / "data" / "raw" / "phiusiil" / "phiusiil.zip")
    parser.add_argument("--output", type=Path, default=PROJECT_ROOT / "data" / "processed" / "urls" / "urls.csv")
    args = parser.parse_args()
    preprocess(args.input, args.output)


if __name__ == "__main__":
    main()
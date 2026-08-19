"""Train a deployable URL model using only shared real-time URL features."""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import joblib
import pandas as pd
import sklearn
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, average_precision_score, confusion_matrix, f1_score, precision_score, recall_score, roc_auc_score
from sklearn.model_selection import train_test_split

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from backend.config import MODEL_DIR, PROJECT_ROOT
from backend.services.url_features import FEATURE_NAMES


def metrics(model, features, labels) -> dict:
    predictions = model.predict(features)
    probabilities = model.predict_proba(features)[:, 1]
    matrix = confusion_matrix(labels, predictions, labels=[0, 1])
    tn, fp, fn, tp = matrix.ravel()
    return {
        "accuracy": round(float(accuracy_score(labels, predictions)), 6),
        "precision": round(float(precision_score(labels, predictions, zero_division=0)), 6),
        "recall": round(float(recall_score(labels, predictions, zero_division=0)), 6),
        "f1": round(float(f1_score(labels, predictions, zero_division=0)), 6),
        "roc_auc": round(float(roc_auc_score(labels, probabilities)), 6),
        "pr_auc": round(float(average_precision_score(labels, probabilities)), 6),
        "confusion_matrix": matrix.tolist(),
        "false_positive_rate": round(float(fp / max(tn + fp, 1)), 6),
        "false_negative_rate": round(float(fn / max(fn + tp, 1)), 6),
    }


def train(dataset: Path) -> dict:
    frame = pd.read_csv(dataset).dropna(subset=["label"])
    missing = [name for name in FEATURE_NAMES if name not in frame.columns]
    if missing:
        raise ValueError(f"Processed URL data is missing shared features: {missing}")
    labels = frame["label"].astype(int)
    features = frame[FEATURE_NAMES]
    train_features, test_features, train_labels, test_labels = train_test_split(features, labels, test_size=0.2, random_state=42, stratify=labels)
    candidates = {
        "logistic_regression": LogisticRegression(max_iter=2000, class_weight="balanced", random_state=42),
        "random_forest": RandomForestClassifier(n_estimators=250, class_weight="balanced", random_state=42, n_jobs=-1),
    }
    candidate_metrics = {}
    for name, model in candidates.items():
        model.fit(train_features, train_labels)
        candidate_metrics[name] = metrics(model, test_features, test_labels)
    selected = max(candidate_metrics, key=lambda name: (candidate_metrics[name]["f1"], candidate_metrics[name]["recall"], name == "logistic_regression"))
    model = candidates[selected]
    MODEL_DIR.mkdir(parents=True, exist_ok=True)
    joblib.dump(model, MODEL_DIR / "url_model.joblib")
    metadata = {
        "algorithm": selected,
        "features": FEATURE_NAMES,
        "dataset": str(dataset),
        "label_mapping": {"0": "LEGITIMATE", "1": "PHISHING"},
        "trained_at": datetime.now(timezone.utc).isoformat(),
        "scikit_learn_version": sklearn.__version__,
        "selected_metrics": candidate_metrics[selected],
        "candidate_metrics": candidate_metrics,
    }
    (MODEL_DIR / "url_model_metadata.json").write_text(json.dumps(metadata, indent=2), encoding="utf-8")
    reports = PROJECT_ROOT / "reports"
    reports.mkdir(exist_ok=True)
    (reports / "url_model_metrics.json").write_text(json.dumps(metadata, indent=2), encoding="utf-8")
    (reports / "url_model_evaluation.md").write_text("# URL model evaluation\n\n```json\n" + json.dumps(candidate_metrics, indent=2) + "\n```\n", encoding="utf-8")
    return metadata


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset", type=Path, default=PROJECT_ROOT / "data" / "processed" / "urls" / "urls.csv")
    args = parser.parse_args()
    if not args.dataset.exists():
        raise SystemExit(f"Processed URL dataset not found: {args.dataset}. Run preprocess_url_data.py first.")
    print(json.dumps(train(args.dataset), indent=2))
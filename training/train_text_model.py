"""Train and compare lightweight text classifiers from processed real data."""

from __future__ import annotations
import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import joblib
import matplotlib.pyplot as plt
import pandas as pd
import sklearn
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    average_precision_score,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
)
from sklearn.model_selection import train_test_split
from sklearn.svm import LinearSVC

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from backend.config import MODEL_DIR, PROJECT_ROOT

RANDOM_STATE = 42

def evaluate(model, features, labels) -> dict:
    predictions = model.predict(features)
    decision = model.decision_function(features)
    positive_score = decision if decision.ndim == 1 else decision[:, 1]
    matrix = confusion_matrix(labels, predictions, labels=[0, 1])
    true_negative, false_positive, false_negative, true_positive = matrix.ravel()
    return {
        "accuracy": round(float(accuracy_score(labels, predictions)), 6),
        "precision": round(float(precision_score(labels, predictions, zero_division=0)), 6),
        "recall": round(float(recall_score(labels, predictions, zero_division=0)), 6),
        "f1": round(float(f1_score(labels, predictions, zero_division=0)), 6),
        "roc_auc": round(float(roc_auc_score(labels, positive_score)), 6),
        "pr_auc": round(float(average_precision_score(labels, positive_score)), 6),
        "confusion_matrix": matrix.tolist(),
        "phishing_recall": round(float(true_positive / max(true_positive + false_negative, 1)), 6),
        "false_positive_rate": round(float(false_positive / max(false_positive + true_negative, 1)), 6),
        "false_negative_rate": round(float(false_negative / max(false_negative + true_positive, 1)), 6),
    }

def train_model(dataset_path: Path) -> dict:
    frame = pd.read_csv(dataset_path).dropna(subset=["text", "label"])
    frame = frame.drop_duplicates(subset=["text"]).reset_index(drop=True)
    labels = frame["label"].astype(int)
    if labels.nunique() != 2:
        raise ValueError("Text training requires exactly two labels: 0=LEGITIMATE and 1=MALICIOUS")
    train_text, test_text, train_labels, test_labels = train_test_split(
        frame["text"], labels, test_size=0.2, random_state=RANDOM_STATE, stratify=labels
    )
    """
# ============================================================
# CONFIGURATION
# ============================================================

DATASET_PATH = "training/data/phishing_email.csv"

MODEL_DIR = "models"

MODEL_PATH = os.path.join(MODEL_DIR, "text_model.joblib")
VECTORIZER_PATH = os.path.join(MODEL_DIR, "text_vectorizer.joblib")
METRICS_PATH = os.path.join(MODEL_DIR, "text_metrics.json")
CONFUSION_MATRIX_PATH = os.path.join(MODEL_DIR, "confusion_matrix.png")


# ============================================================
# LOAD DATASET
# ============================================================

def load_dataset():
    print("\nLoading dataset...")

    df = pd.read_csv(DATASET_PATH)

    print(f"Dataset shape: {df.shape}")

    # Keep only required columns
    df = df[["text_combined", "label"]]

    # Remove missing values
    df = df.dropna(subset=["text_combined", "label"])

    # Remove duplicate emails
    df = df.drop_duplicates(subset=["text_combined"])

    # Convert text to string
    df["text_combined"] = df["text_combined"].astype(str)

    # Make sure labels are integers
    df["label"] = df["label"].astype(int)

    print(f"Dataset after cleaning: {df.shape}")

    print("\nClass distribution:")
    print(df["label"].value_counts())

    return df


# ============================================================
# TRAIN MODEL
# ============================================================

def train_model():

    df = load_dataset()

    X = df["text_combined"]
    y = df["label"]

    # --------------------------------------------------------
    # Train / Test Split
    # --------------------------------------------------------

    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=0.20,
        random_state=42,
        stratify=y,
    )

    print("\nTraining samples:", len(X_train))
    print("Testing samples:", len(X_test))

    # --------------------------------------------------------
    # TF-IDF
    # --------------------------------------------------------

    print("\nCreating TF-IDF features...")

    vectorizer = TfidfVectorizer(
        ngram_range=(1, 2),
        min_df=2,
        max_df=0.95,
        sublinear_tf=True,
        max_features=150000,
    )

    X_train_vec = vectorizer.fit_transform(X_train)
    X_test_vec = vectorizer.transform(X_test)

    print("TF-IDF training shape:", X_train_vec.shape)
    print("TF-IDF testing shape:", X_test_vec.shape)

    # --------------------------------------------------------
    # Logistic Regression
    # --------------------------------------------------------

    print("\nTraining Logistic Regression model...")

    model = LogisticRegression(
        max_iter=1000,
        class_weight="balanced",
        random_state=42,
    )

    model.fit(X_train_vec, y_train)

    print("Model training completed.")

    # --------------------------------------------------------
    # Predictions
    # --------------------------------------------------------

    y_pred = model.predict(X_test_vec)
    y_prob = model.predict_proba(X_test_vec)[:, 1]

    # --------------------------------------------------------
    # Metrics
    # --------------------------------------------------------

    accuracy = accuracy_score(y_test, y_pred)
    precision = precision_score(y_test, y_pred, zero_division=0)
    recall = recall_score(y_test, y_pred, zero_division=0)
    f1 = f1_score(y_test, y_pred, zero_division=0)
    roc_auc = roc_auc_score(y_test, y_prob)

    metrics = {
        "dataset_size": int(len(df)),
        "training_samples": int(len(X_train)),
        "testing_samples": int(len(X_test)),
        "accuracy": round(float(accuracy), 4),
        "precision": round(float(precision), 4),
        "recall": round(float(recall), 4),
        "f1_score": round(float(f1), 4),
        "roc_auc": round(float(roc_auc), 4),
        "confusion_matrix": confusion_matrix(y_test, y_pred).tolist(),
    }

    # --------------------------------------------------------
    # Print Results
    # --------------------------------------------------------

    print("\n" + "=" * 60)
    print("MODEL PERFORMANCE")
    print("=" * 60)

    print(f"Accuracy :  {accuracy:.4f}")
    print(f"Precision:  {precision:.4f}")
    print(f"Recall   :  {recall:.4f}")
    print(f"F1 Score :  {f1:.4f}")
    print(f"ROC-AUC  :  {roc_auc:.4f}")

    print("\nClassification Report:")
    print(classification_report(
        y_test,
        y_pred,
        target_names=["Legitimate", "Phishing"],
        zero_division=0,
    ))

    # --------------------------------------------------------
    # Confusion Matrix
    # --------------------------------------------------------

    cm = confusion_matrix(y_test, y_pred)

    plt.figure(figsize=(7, 5))

    sns.heatmap(
        cm,
        annot=True,
        fmt="d",
        xticklabels=["Legitimate", "Phishing"],
        yticklabels=["Legitimate", "Phishing"],
    )

    plt.title("PhishExplain AI - Confusion Matrix")
    plt.xlabel("Predicted")
    plt.ylabel("Actual")
    plt.tight_layout()

    # --------------------------------------------------------
    # Save everything
    # --------------------------------------------------------

    os.makedirs(MODEL_DIR, exist_ok=True)

    joblib.dump(model, MODEL_PATH)
    joblib.dump(vectorizer, VECTORIZER_PATH)

    with open(METRICS_PATH, "w", encoding="utf-8") as file:
        json.dump(metrics, file, indent=2)

    plt.savefig(CONFUSION_MATRIX_PATH, dpi=150)
    plt.close()

    print("\n" + "=" * 60)
    print("FILES SAVED")
    print("=" * 60)

    print(f"Model      : {MODEL_PATH}")
    print(f"Vectorizer : {VECTORIZER_PATH}")
    print(f"Metrics    : {METRICS_PATH}")
    print(f"Confusion  : {CONFUSION_MATRIX_PATH}")

        """

    vectorizer = TfidfVectorizer(ngram_range=(1, 2), min_df=2, sublinear_tf=True)
    train_features = vectorizer.fit_transform(train_text)
    test_features = vectorizer.transform(test_text)
    candidates = {
        "logistic_regression": LogisticRegression(max_iter=2000, class_weight="balanced", random_state=RANDOM_STATE),
        "linear_svm": LinearSVC(class_weight="balanced", random_state=RANDOM_STATE),
    }
    metrics = {}
    for name, model in candidates.items():
        model.fit(train_features, train_labels)
        metrics[name] = evaluate(model, test_features, test_labels)

    # Logistic Regression remains the deployable choice when performance is tied
    # because calibrated probabilities and coefficient-based XAI are part of the API.
    selected_name = max(metrics, key=lambda name: (metrics[name]["f1"], metrics[name]["phishing_recall"], name == "logistic_regression"))
    if selected_name != "logistic_regression":
        raise RuntimeError(
            "Linear SVM outperformed Logistic Regression; review calibration/XAI before selecting it for deployment."
        )
    model = candidates[selected_name]
    MODEL_DIR.mkdir(parents=True, exist_ok=True)
    joblib.dump(model, MODEL_DIR / "text_model.joblib")
    joblib.dump(vectorizer, MODEL_DIR / "text_vectorizer.joblib")

    metadata = {
    "algorithm": selected_name,
    "feature_configuration": {"ngram_range": [1, 2], "min_df": 2, "sublinear_tf": True},
    "dataset_path": str(dataset_path),
    "dataset_sources": sorted(frame.get("source", pd.Series(dtype=str)).dropna().unique().tolist()),
    "label_mapping": {"0": "LEGITIMATE", "1": "MALICIOUS"},
    "random_state": RANDOM_STATE,
    "trained_at": datetime.now(timezone.utc).isoformat(),
    "scikit_learn_version": sklearn.__version__,
    "selected_metrics": metrics[selected_name],
        "candidate_metrics": metrics,
        "n_rows": int(len(frame)),
        "n_features": int(len(vectorizer.get_feature_names_out())),
    }
    (MODEL_DIR / "text_model_metadata.json").write_text(json.dumps(metadata, indent=2), encoding="utf-8")
    reports_dir = PROJECT_ROOT / "reports"
    reports_dir.mkdir(exist_ok=True)
    (reports_dir / "text_model_metrics.json").write_text(json.dumps(metadata, indent=2), encoding="utf-8")
    (reports_dir / "text_model_evaluation.md").write_text(
        "# Text model evaluation\n\n"
    f"Selected model: `{selected_name}`\n\n"
    "Metrics are generated from the held-out split by this script.\n\n"
    "```json\n" + json.dumps(metrics, indent=2) + "\n```\n",
        encoding="utf-8",
    )
    return metadata

def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset", type=Path, default=PROJECT_ROOT / "data" / "processed" / "text" / "messages.csv")
    args = parser.parse_args()
    if not args.dataset.exists():
        raise SystemExit(f"Processed dataset not found: {args.dataset}. Run preprocess_text_data.py first.")
    print(json.dumps(train_model(args.dataset), indent=2))

# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":
    main()

from __future__ import annotations

import json
import os

import joblib
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, confusion_matrix, f1_score, precision_score, recall_score, roc_auc_score
from sklearn.model_selection import train_test_split


DATASET = [
    ("Your account will be suspended. Verify your password immediately.", 1),
    ("Urgent action required. Login now to secure your account.", 1),
    ("We detected suspicious activity. Please confirm your credentials.", 1),
    ("Password reset required immediately. Click here to verify.", 1),
    ("Your account has been locked. Update your password today.", 1),
    ("Invoice due. Complete payment before midnight.", 1),
    ("Security alert. Your OTP is required to proceed.", 1),
    ("Thanks for meeting today. Please send the notes when you have time.", 0),
    ("The project status is on track and the deadline is next Friday.", 0),
    ("Your package was delivered successfully and the receipt is attached.", 0),
    ("We discussed the summary in the meeting and the next steps are clear.", 0),
    ("Please review the attached report before the end of the week.", 0),
    ("The invoice was sent and the payment date is next month.", 0),
]


def train_model() -> dict:
    df = pd.DataFrame(DATASET, columns=["text", "label"])
    df = df.drop_duplicates().reset_index(drop=True)
    X_train, X_test, y_train, y_test = train_test_split(df["text"], df["label"], test_size=0.3, random_state=42, stratify=df["label"])

    vectorizer = TfidfVectorizer(ngram_range=(1, 2))
    X_train_vec = vectorizer.fit_transform(X_train)
    X_test_vec = vectorizer.transform(X_test)

    model = LogisticRegression(max_iter=1000)
    model.fit(X_train_vec, y_train)
    y_pred = model.predict(X_test_vec)
    y_prob = model.predict_proba(X_test_vec)[:, 1]

    metrics = {
        "accuracy": round(float(accuracy_score(y_test, y_pred)), 4),
        "precision": round(float(precision_score(y_test, y_pred, zero_division=0)), 4),
        "recall": round(float(recall_score(y_test, y_pred, zero_division=0)), 4),
        "f1": round(float(f1_score(y_test, y_pred, zero_division=0)), 4),
        "roc_auc": round(float(roc_auc_score(y_test, y_prob)), 4),
        "confusion_matrix": confusion_matrix(y_test, y_pred).tolist(),
    }

    os.makedirs("models", exist_ok=True)
    joblib.dump(model, "models/text_model.joblib")
    joblib.dump(vectorizer, "models/text_vectorizer.joblib")
    with open("models/text_metrics.json", "w", encoding="utf-8") as fh:
        json.dump(metrics, fh, indent=2)
    return metrics


if __name__ == "__main__":
    print(train_model())

from __future__ import annotations

import os
import pickle
from typing import Any

import joblib
import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression


class TextClassifier:
    """TF-IDF + logistic regression text classifier with a simple fallback."""

    MODEL_PATH = os.path.join("models", "text_model.joblib")
    VECTOR_PATH = os.path.join("models", "text_vectorizer.joblib")

    def __init__(self, model_path: str | None = None, vector_path: str | None = None):
        self.model_path = model_path or self.MODEL_PATH
        self.vector_path = vector_path or self.VECTOR_PATH
        self.model = None
        self.vectorizer = None
        self._load_or_initialize()

    def _load_or_initialize(self):
        if os.path.exists(self.model_path) and os.path.exists(self.vector_path):
            self.model = joblib.load(self.model_path)
            self.vectorizer = joblib.load(self.vector_path)
            return

        # deterministic prototype model to keep the project working without training data
        self.vectorizer = TfidfVectorizer(ngram_range=(1, 2), min_df=1)
        phishing_texts = [
            "Your account will be suspended. Verify your password immediately.",
            "Urgent action required. Login now to secure your account.",
            "We detected suspicious activity. Please confirm your credentials.",
            "Password reset required immediately. Click here to verify.",
            "Your account has been locked. Update your password today.",
            "Invoice due. Complete payment before midnight.",
            "Security alert. Your OTP is required to proceed.",
        ]
        safe_texts = [
            "Thanks for meeting today. Please send the notes when you have time.",
            "The project status is on track and the deadline is next Friday.",
            "Your package was delivered successfully and the receipt is attached.",
            "We discussed the summary in the meeting and the next steps are clear.",
            "Please review the attached report before the end of the week.",
            "The invoice was sent and the payment date is next month.",
        ]
        texts = phishing_texts + safe_texts
        labels = [1] * len(phishing_texts) + [0] * len(safe_texts)
        X = self.vectorizer.fit_transform(texts)
        self.model = LogisticRegression(max_iter=1000)
        self.model.fit(X, labels)
        os.makedirs(os.path.dirname(self.model_path), exist_ok=True)
        joblib.dump(self.model, self.model_path)
        joblib.dump(self.vectorizer, self.vector_path)

    def predict(self, text: str) -> dict[str, Any]:
        cleaned = (text or "").strip()
        if not cleaned:
            return {"label": "SAFE", "probability": 0.05, "confidence": 0.05}

        features = self.vectorizer.transform([cleaned])
        prob = float(self.model.predict_proba(features)[0, 1])
        label = "PHISHING" if prob >= 0.5 else "SAFE"
        return {"label": label, "probability": round(prob, 4), "confidence": round(prob, 4)}

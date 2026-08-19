from __future__ import annotations

from pathlib import Path
from typing import Any

import joblib
import pandas as pd

from backend.config import MODEL_DIR
from backend.services.url_features import FEATURE_NAMES, extract_url_features


class URLClassifier:
    def __init__(self, model_path: str | Path | None = None):
        self.model_path = Path(model_path or (MODEL_DIR / "url_model.joblib"))
        self.model: Any | None = None
        if self.model_path.exists():
            try:
                self.model = joblib.load(self.model_path)
            except Exception:
                self.model = None

    def predict(self, url: str | None) -> dict[str, Any]:
        if not url or self.model is None:
            return {"available": False, "label": "UNAVAILABLE", "probability": None}
        features = extract_url_features(url)
        values = pd.DataFrame([[features[name] for name in FEATURE_NAMES]], columns=FEATURE_NAMES)
        probability = float(self.model.predict_proba(values)[0, 1])
        return {
            "available": True,
            "label": "PHISHING" if probability >= 0.5 else "LEGITIMATE",
            "probability": round(probability, 4),
        }
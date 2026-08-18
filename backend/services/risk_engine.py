from __future__ import annotations

from typing import Any


STANDARD_WEIGHTS = {
    "text_probability": 0.55,
    "url_risk": 0.25,
    "indicator_weight": 0.20,
}


def compute_risk_score(text_probability: float, url_risk: float = 0.0, indicators: list[dict[str, Any]] | None = None, weights: dict[str, float] | None = None) -> dict:
    weights = weights or STANDARD_WEIGHTS
    indicator_count = len(indicators or [])
    indicator_signal = min(indicator_count * 12, 30)

    total = (
        text_probability * 100 * weights["text_probability"]
        + url_risk * weights["url_risk"]
        + indicator_signal * weights["indicator_weight"]
    )
    risk_score = max(0, min(int(round(total)), 100))

    if risk_score <= 30:
        level = "LOW"
        label = "Likely Safe"
    elif risk_score <= 60:
        level = "MEDIUM"
        label = "Suspicious — Verify"
    elif risk_score <= 80:
        level = "HIGH"
        label = "High Risk"
    else:
        level = "CRITICAL"
        label = "Likely Phishing"

    return {
        "risk_score": risk_score,
        "level": level,
        "label": label,
        "weights": weights,
        "indicator_signal": indicator_signal,
    }

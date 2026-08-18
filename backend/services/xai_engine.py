from __future__ import annotations

from typing import Any


FEATURE_IMPORTANCE = {
    "password": 0.21,
    "immediately": 0.18,
    "suspended": 0.16,
    "verify": 0.14,
    "account": 0.12,
    "click": 0.1,
    "urgent": 0.09,
    "otp": 0.08,
    "login": 0.07,
    "confirm": 0.06,
}


def compute_model_feature_contributions(text: str) -> list[dict[str, Any]]:
    content = (text or "").lower()
    if not content:
        return []

    findings = []
    for feature, impact in FEATURE_IMPORTANCE.items():
        if feature in content:
            findings.append({"feature": feature, "impact": round(impact, 2)})
    return sorted(findings, key=lambda item: item["impact"], reverse=True)[:6]


def explain_feature_contributions(findings: list[dict[str, Any]]) -> str:
    if not findings:
        return "The model did not identify strong phishing-related language in the message."
    top = findings[0]
    return (
        f"The model strongly associated {', '.join(item['feature'] for item in findings[:3])} with phishing behavior."
        f" The strongest contribution was {top['feature']} (impact {top['impact']})."
    )

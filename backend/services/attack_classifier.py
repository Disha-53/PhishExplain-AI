from __future__ import annotations


def classify_attack(indicators: list[dict] | None, url_analysis: dict | None = None) -> str:
    names = [item.get("name", "") for item in (indicators or [])]
    if "Credential request" in names or "Link action" in names:
        return "Credential Phishing"
    if "Urgency" in names and "Threat" in names:
        return "Spearphishing"
    if url_analysis and url_analysis.get("risk_score", 0) >= 60:
        return "Malicious Link Phishing"
    return "General Phishing"

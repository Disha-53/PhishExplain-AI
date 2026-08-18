from __future__ import annotations

import re
from typing import Any


RULES = {
    "Urgency": ["immediately", "urgent", "act now", "within 24 hours"],
    "Threat": ["suspended", "blocked", "terminated", "legal action", "restricted"],
    "Credential request": ["password", "otp", "login", "verification code", "verify your password", "credentials"],
    "Financial pressure": ["payment", "refund", "invoice", "bank", "transfer"],
    "Link action": ["click here", "verify now", "login here"],
    "Impersonation": ["bank", "paypal", "microsoft", "google", "apple", "amazon", "delivery", "cloud"]
}


def detect_indicators(text: str) -> list[dict[str, Any]]:
    content = (text or "").lower().strip()
    if not content:
        return []

    findings = []
    for name, keywords in RULES.items():
        hits = [kw for kw in keywords if kw in content]
        if hits:
            finding = {
                "name": name,
                "severity": "HIGH" if name in {"Credential request", "Threat", "Urgency"} else "MEDIUM",
                "evidence": hits[:5],
            }
            findings.append(finding)
    return findings

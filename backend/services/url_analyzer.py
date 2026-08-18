from __future__ import annotations

import re
from urllib.parse import urlparse


SUSPICIOUS_TLDS = {"tk", "xyz", "club", "top", "bid", "loan", "cf"}
SHORTENER_DOMAINS = {"bit.ly", "tinyurl.com", "goo.gl", "t.co", "ow.ly", "is.gd"}


def _safe_url(value: str) -> str:
    return (value or "").strip()


def analyze_url(url: str | None) -> dict:
    raw = _safe_url(url)
    if not raw:
        return {
            "risk_score": 0,
            "label": "LOW",
            "facts": [],
            "summary": "No URL provided.",
            "is_valid": False,
        }

    score = 0
    facts = []
    is_valid = True

    try:
        parsed = urlparse(raw if raw.startswith(("http://", "https://")) else "https://" + raw)
    except Exception:
        parsed = None
        is_valid = False

    if not parsed or not parsed.netloc:
        is_valid = False
        score += 20
        facts.append("Malformed URL format detected.")

    if parsed:
        hostname = parsed.hostname or ""
        if parsed.scheme.lower() == "http":
            score += 15
            facts.append("HTTP is used rather than HTTPS.")
        if parsed.scheme.lower() == "https":
            facts.append("HTTPS is present.")
        if re.search(r"\d+\.\d+\.\d+\.\d+", hostname):
            score += 25
            facts.append("IP address used instead of a hostname.")
        if len(raw) > 100:
            score += 15
            facts.append("URL length is unusually long.")
        if raw.count(".") > 4:
            score += 10
            facts.append("Multiple dots suggest excessive subdomain nesting.")
        if raw.count("-") > 3:
            score += 8
            facts.append("Multiple hyphens in the URL structure.")
        if hostname and hostname.split(".")[-1].lower() in SUSPICIOUS_TLDS:
            score += 20
            facts.append("Suspicious top-level domain detected.")
        if hostname and any(hostname.lower().endswith(domain) for domain in SHORTENER_DOMAINS):
            score += 25
            facts.append("URL shortener domain detected.")
        if re.search(r"%[0-9A-Fa-f]{2}", raw):
            score += 10
            facts.append("Encoded characters detected.")
        if parsed.port and parsed.port not in {80, 443}:
            score += 12
            facts.append("Uncommon port detected.")
        if parsed.path and parsed.path.count("/") > 4:
            score += 8
            facts.append("Excessive path depth detected.")
        suspicious_keywords = ["verify", "login", "secure", "update", "account", "confirm", "password", "bank", "portal" ]
        if any(word in raw.lower() for word in suspicious_keywords):
            score += 12
            facts.append("Suspicious keywords suggest a phishing-style landing page.")

    if score >= 80:
        label = "CRITICAL"
    elif score >= 60:
        label = "HIGH"
    elif score >= 30:
        label = "MEDIUM"
    else:
        label = "LOW"

    if parsed and parsed.scheme.lower() == "https" and not facts:
        summary = "HTTPS is used and no strong URL anomalies were detected."
    elif parsed and parsed.scheme.lower() == "https":
        summary = "HTTPS is used, but some URL risk indicators were detected."
    elif facts:
        summary = "Static URL analysis detected suspicious characteristics."
    else:
        summary = "No strong URL anomalies detected."

    return {
        "risk_score": min(score, 100),
        "label": label,
        "facts": facts,
        "summary": summary,
        "is_valid": is_valid,
    }

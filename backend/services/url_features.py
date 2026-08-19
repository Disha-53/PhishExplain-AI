from __future__ import annotations

import math
import re
from collections import Counter
from urllib.parse import urlparse


FEATURE_NAMES = [
    "url_length", "hostname_length", "path_length", "query_length", "dot_count",
    "hyphen_count", "digit_count", "special_character_count", "subdomain_depth",
    "uses_https", "is_ip_hostname", "encoded_character_count", "url_entropy",
    "suspicious_keyword_count", "punycode_indicator", "uncommon_port", "path_depth",
]
SUSPICIOUS_KEYWORDS = ("verify", "login", "secure", "update", "account", "confirm", "password", "bank", "portal")


def extract_url_features(url: str | None) -> dict[str, float]:
    raw = (url or "").strip()
    parsed = urlparse(raw if raw.startswith(("http://", "https://")) else f"https://{raw}")
    hostname = parsed.hostname or ""
    characters = Counter(raw)
    entropy = 0.0
    if raw:
        entropy = -sum((count / len(raw)) * math.log2(count / len(raw)) for count in characters.values())
    is_ip = bool(re.fullmatch(r"\d{1,3}(?:\.\d{1,3}){3}", hostname))
    return {
        "url_length": float(len(raw)),
        "hostname_length": float(len(hostname)),
        "path_length": float(len(parsed.path)),
        "query_length": float(len(parsed.query)),
        "dot_count": float(raw.count(".")),
        "hyphen_count": float(raw.count("-")),
        "digit_count": float(sum(character.isdigit() for character in raw)),
        "special_character_count": float(sum(not character.isalnum() for character in raw)),
        "subdomain_depth": float(max(0, len(hostname.split(".")) - 2)) if hostname else 0.0,
        "uses_https": float(parsed.scheme.lower() == "https"),
        "is_ip_hostname": float(is_ip),
        "encoded_character_count": float(len(re.findall(r"%[0-9a-fA-F]{2}", raw))),
        "url_entropy": entropy,
        "suspicious_keyword_count": float(sum(keyword in raw.lower() for keyword in SUSPICIOUS_KEYWORDS)),
        "punycode_indicator": float("xn--" in hostname.lower()),
        "uncommon_port": float(bool(parsed.port and parsed.port not in {80, 443})),
        "path_depth": float(max(0, parsed.path.count("/") - 1)),
    }


def feature_matrix(urls: list[str]) -> list[list[float]]:
    return [[features[name] for name in FEATURE_NAMES] for features in (extract_url_features(url) for url in urls)]
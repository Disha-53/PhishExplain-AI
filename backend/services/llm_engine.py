from __future__ import annotations

import os
from typing import Any


class LLMExplanationEngine:
    def __init__(self):
        self.api_key = os.getenv("LLM_API_KEY") or os.getenv("OPENAI_API_KEY")

    def is_available(self) -> bool:
        return bool(self.api_key)

    def generate(self, structured: dict[str, Any]) -> dict[str, str]:
        if not self.api_key:
            return self._fallback(structured)
        return self._fallback(structured)

    def _fallback(self, structured: dict[str, Any]) -> dict[str, str]:
        label = structured.get("label", "LIKELY PHISHING")
        risk_score = structured.get("risk_score", 0)
        indicators = structured.get("indicators", [])
        attack_type = structured.get("attack_type", "Credential Phishing")
        explanation_bits = []
        if indicators:
            explanation_bits = [str(item).lower() for item in indicators[:3]]
        risk_text = "This message is considered high risk" if risk_score >= 60 else "This message shows some suspicious patterns"
        if explanation_bits:
            summary = f"{risk_text} because it contains {', '.join(explanation_bits)}. The included URL and message context also suggest a phishing attempt."
        else:
            summary = f"{risk_text} because it contains urgency, credential-related language, and a potentially suspicious link."

        recommendation = (
            "Do not click the link or respond directly. Verify the request through the organization\'s official website or a trusted contact method."
        )
        return {
            "attack_type": attack_type,
            "explanation": summary,
            "recommendation": recommendation,
        }

from __future__ import annotations

from fastapi import APIRouter, HTTPException

from backend.schemas.analysis import AnalysisRequest
from backend.services.attack_classifier import classify_attack
from backend.services.llm_engine import LLMExplanationEngine
from backend.services.rag_engine import RAGEngine
from backend.services.rule_engine import detect_indicators
from backend.services.risk_engine import compute_risk_score
from backend.services.text_classifier import TextClassifier
from backend.services.url_analyzer import analyze_url
from backend.services.xai_engine import compute_model_feature_contributions, explain_feature_contributions
from backend.utils.logging_config import get_logger

router = APIRouter()
logger = get_logger("analyze")

_text_model = TextClassifier()
_rag = RAGEngine()
_llm = LLMExplanationEngine()


@router.post("/analyze")
def analyze(payload: AnalysisRequest):
    try:
        text = payload.text or ""
        url = payload.url or ""
        logger.info("analysis_started")

        if not text.strip() and not url.strip():
            return {
                "label": "SAFE",
                "risk_score": 0,
                "severity": "LOW",
                "attack_type": "None detected",
                "indicators": [],
                "xai": [],
                "url_analysis": {"risk_score": 0, "label": "LOW", "facts": [], "summary": "No input supplied."},
                "knowledge": {"source": "fallback", "results": []},
                "explanation": "No meaningful message or URL was provided for analysis.",
                "recommendation": "Paste a message or URL to evaluate it.",
            }

        text_result = _text_model.predict(text)
        url_result = analyze_url(url)
        indicators = detect_indicators(text)
        risk = compute_risk_score(
            text_probability=text_result["probability"],
            url_risk=url_result.get("risk_score", 0) / 100,
            indicators=indicators,
        )

        xai = compute_model_feature_contributions(text)
        summary = explain_feature_contributions(xai)
        if not indicators:
            summary = "The model did not identify strong phishing indicators in the message."

        attack_type = classify_attack(indicators, url_result)
        query = " ".join([item["name"] for item in indicators]) + " " + (url or "")
        knowledge = _rag.retrieve(query)

        label = "LIKELY PHISHING" if risk["risk_score"] >= 60 else "LIKELY SAFE"
        severity = "CRITICAL" if risk["risk_score"] >= 81 else "HIGH" if risk["risk_score"] >= 61 else "MEDIUM" if risk["risk_score"] >= 31 else "LOW"

        structured = {
            "label": label,
            "risk_score": risk["risk_score"],
            "attack_type": attack_type,
            "indicators": [item["name"] for item in indicators],
            "xai": xai,
            "url_analysis": url_result,
            "knowledge": knowledge,
            "explanation": summary,
            "recommendation": "Do not click the link or respond directly. Verify the request through official channels.",
        }

        llm_result = _llm.generate(structured)
        response = {
            "label": label,
            "risk_score": risk["risk_score"],
            "severity": severity,
            "attack_type": llm_result.get("attack_type", attack_type),
            "indicators": [item["name"] for item in indicators],
            "xai": xai,
            "url_analysis": url_result,
            "knowledge": knowledge,
            "explanation": llm_result.get("explanation", summary),
            "recommendation": llm_result.get("recommendation", "Verify independently using official channels."),
        }
        logger.info("analysis_completed", extra={"risk_score": response["risk_score"]})
        return response
    except Exception as exc:
        logger.exception("analysis_failed")
        raise HTTPException(status_code=500, detail="Analysis failed") from exc

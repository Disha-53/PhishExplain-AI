from __future__ import annotations

from typing import Any


def compute_model_feature_contributions(
    text: str,
    model: Any | None = None,
    vectorizer: Any | None = None,
    limit: int = 6,
) -> list[dict[str, Any]]:
    """Return observed TF-IDF feature contributions toward phishing.

    Contributions are evidence from the fitted linear model, not causal claims
    or hidden model reasoning. Positive values support phishing; negative values
    support the safe class.
    """
    content = (text or "").strip()
    if not content or model is None or vectorizer is None:
        return []
    if not hasattr(model, "coef_") or not hasattr(vectorizer, "get_feature_names_out"):
        return []

    transformed = vectorizer.transform([content])
    feature_names = vectorizer.get_feature_names_out()
    coefficients = model.coef_
    classes = list(getattr(model, "classes_", [0, 1]))
    phishing_index = classes.index(1) if 1 in classes else 0
    weights = coefficients[0] if coefficients.shape[0] == 1 else coefficients[phishing_index]
    values = transformed.toarray()[0]
    contributions = values * weights
    observed = [
        (index, float(contribution))
        for index, contribution in enumerate(contributions)
        if values[index] > 0 and contribution != 0
    ]
    observed.sort(key=lambda item: abs(item[1]), reverse=True)
    results = []
    for index, contribution in observed[:limit]:
        direction = "positive" if contribution > 0 else "negative"
        results.append(
            {
                "feature": str(feature_names[index]),
                "impact": round(contribution, 4),
                "direction": direction,
                "description": (
                    "This observed feature contributed toward the phishing classification."
                    if contribution > 0
                    else "This observed feature contributed toward the legitimate classification."
                ),
            }
        )
    return results


def explain_feature_contributions(findings: list[dict[str, Any]]) -> str:
    positive = [item for item in findings if item.get("direction") == "positive"]
    if not positive:
        return "The fitted text model did not produce positive phishing feature evidence for this message."
    features = ", ".join(item["feature"] for item in positive[:3])
    return f"The fitted text model found phishing-associated feature evidence in: {features}."

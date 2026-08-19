from backend.services.risk_engine import compute_risk_score


def test_safe_text_and_url_stay_low():
    result = compute_risk_score(text_probability=0.05, url_risk=0)
    assert result["risk_score"] <= 10


def test_high_risk_text_with_safe_url():
    result = compute_risk_score(text_probability=0.95, url_risk=0)
    assert result["risk_score"] >= 50


def test_safe_text_with_high_risk_url_contributes():
    result = compute_risk_score(text_probability=0.05, url_risk=100)
    assert result["risk_score"] >= 20


def test_high_risk_text_and_url_are_combined():
    result = compute_risk_score(text_probability=0.95, url_risk=100)
    assert result["risk_score"] > compute_risk_score(text_probability=0.95, url_risk=0)["risk_score"]


def test_missing_module_results_are_safe_defaults():
    result = compute_risk_score()
    assert result["risk_score"] == 0
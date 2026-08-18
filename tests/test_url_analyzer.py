from backend.services.url_analyzer import analyze_url


def test_https_url():
    result = analyze_url("https://example.com/login")
    assert result["risk_score"] >= 0
    assert "https" in result["summary"].lower()


def test_http_url():
    result = analyze_url("http://example-login.com")
    assert result["risk_score"] >= 0


def test_ip_url():
    result = analyze_url("http://192.168.1.10/login")
    assert result["risk_score"] > 0


def test_long_url():
    result = analyze_url("https://example.com/" + "a" * 200)
    assert result["risk_score"] >= 0


def test_malformed_url():
    result = analyze_url("not-a-valid-url")
    assert result["risk_score"] >= 0

from fastapi.testclient import TestClient
from backend.main import app


client = TestClient(app)


def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_valid_request():
    response = client.post("/analyze", json={"text": "Verify your password immediately.", "url": "http://example-login.com"})
    assert response.status_code == 200
    body = response.json()
    assert "label" in body
    assert "risk_score" in body


def test_url_only_request():
    response = client.post("/analyze", json={"text": "", "url": "http://192.168.1.10/login"})
    assert response.status_code == 200
    assert response.json()["url_analysis"]["is_valid"] is True


def test_combined_request_contains_separate_evidence_sections():
    response = client.post("/analyze", json={"text": "Verify your password immediately.", "url": "https://example.com/login"})
    assert response.status_code == 200
    body = response.json()
    assert "indicators" in body
    assert "xai" in body
    assert "knowledge" in body


def test_empty_request():
    response = client.post("/analyze", json={"text": "   ", "url": ""})
    assert response.status_code == 200
    assert response.json()["label"] in {"SAFE", "LIKELY SAFE"}


def test_malformed_request():
    response = client.post("/analyze", data="not-json")
    assert response.status_code in {400, 422}

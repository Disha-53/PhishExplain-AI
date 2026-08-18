from backend.services.rule_engine import detect_indicators


def test_urgency():
    result = detect_indicators("Act now immediately or your account will be suspended.")
    assert any(item["name"] == "Urgency" for item in result)


def test_credential_request():
    result = detect_indicators("Please verify your password and login immediately.")
    assert any(item["name"] == "Credential request" for item in result)


def test_threat():
    result = detect_indicators("Your account has been suspended and blocked.")
    assert any(item["name"] == "Threat" for item in result)


def test_financial_pressure():
    result = detect_indicators("Your invoice is due and refund request requires account verification.")
    assert any(item["name"] == "Financial pressure" for item in result)

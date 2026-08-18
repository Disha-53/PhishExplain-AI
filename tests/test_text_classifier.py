import pytest
from backend.services.text_classifier import TextClassifier


def test_model_loads():
    model = TextClassifier()
    assert model is not None


def test_classifier_predicts():
    model = TextClassifier()
    result = model.predict("Your account will be suspended. Verify your password immediately.")
    assert "probability" in result
    assert 0 <= result["probability"] <= 1


def test_empty_input():
    model = TextClassifier()
    result = model.predict("   ")
    assert result["label"] == "SAFE"

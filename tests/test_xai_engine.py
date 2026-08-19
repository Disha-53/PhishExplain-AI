from backend.services.text_classifier import TextClassifier
from backend.services.xai_engine import compute_model_feature_contributions


def test_xai_uses_fitted_model_vocabulary():
    classifier = TextClassifier()
    result = compute_model_feature_contributions(
        "Verify your password immediately.", classifier.model, classifier.vectorizer
    )
    vocabulary = set(classifier.vectorizer.get_feature_names_out())
    assert result
    assert all(item["feature"] in vocabulary for item in result)
    assert all(item["direction"] in {"positive", "negative"} for item in result)


def test_xai_empty_or_missing_model_is_empty():
    assert compute_model_feature_contributions("verify", None, None) == []
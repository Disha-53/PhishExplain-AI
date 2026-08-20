import joblib

MODEL_PATH = "models/text_model.joblib"
VECTORIZER_PATH = "models/text_vectorizer.joblib"

model = joblib.load(MODEL_PATH)
vectorizer = joblib.load(VECTORIZER_PATH)

test_emails = [
    {
        "name": "Suspicious account email",
        "text": "URGENT! Your bank account will be suspended today. Click here immediately to verify your password."
    },
    {
        "name": "Normal work email",
        "text": "Hi, please find the project report attached. Let's discuss the remaining tasks during tomorrow's meeting."
    },
    {
        "name": "Suspicious security email",
        "text": "We detected unusual activity on your account. Confirm your credentials immediately to avoid account suspension."
    },
    {
        "name": "Normal delivery email",
        "text": "Your package has been delivered. Thank you for shopping with us."
    }
]

texts = [email["text"] for email in test_emails]

features = vectorizer.transform(texts)

predictions = model.predict(features)
probabilities = model.predict_proba(features)

for email, prediction, probability in zip(
    test_emails,
    predictions,
    probabilities
):
    phishing_probability = probability[1]

    print("\n" + "=" * 60)
    print(email["name"])
    print("=" * 60)

    print(
        "Prediction:",
        "PHISHING" if prediction == 1 else "LEGITIMATE"
    )

    print(f"Phishing probability: {phishing_probability:.2%}")
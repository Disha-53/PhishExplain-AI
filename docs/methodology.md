# Methodology

PhishExplain AI uses a transparent pipeline:

- Tokenize and normalize the user message
- Score with TF-IDF + logistic regression
- Check URL characteristics for suspicious behavior
- Detect explicit phishing indicators such as urgency and credential requests
- Combine the results into a weighted risk score
- Retrieve supporting cybersecurity knowledge
- Summarize the result in plain language

The purpose is not to claim absolute certainty. The system communicates risk and evidence while prompting independent verification.

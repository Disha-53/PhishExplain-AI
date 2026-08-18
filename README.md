# PhishExplain AI

## Overview

PhishExplain AI is a local-first browser extension and FastAPI backend designed to detect phishing-like messages and suspicious URLs while explaining the result in plain language. The product combines a machine learning classifier, transparent rule engine, URL analysis, model feature attribution, cybersecurity knowledge retrieval, and a deterministic fallback explanation path.

## Problem

Many phishing detectors return a single label but do not explain why the message looks risky or what a user should do next. This makes detection hard to trust and harder to act on.

## Solution

PhishExplain AI adds a clear chain of evidence:

- ML detection for text risk
- URL risk analysis for suspicious domains and patterns
- Rule engine for urgency, credential requests, threat language, and link actions
- Explainable AI that highlights the most influential words and phrases
- Local cybersecurity knowledge context with attack mapping
- Clear recommendations to help users verify independently and avoid unsafe clicks

## Key Features

- Chrome extension with manual input and page analysis
- Local FastAPI backend at http://127.0.0.1:8000
- TF-IDF + logistic regression text risk model
- Transparent URL risk engine
- Attack indicator detection and risk fusion
- Explainable token-attribution view
- Local knowledge-base retrieval for cybersecurity context
- Deterministic fallback explanation when external AI services are unavailable

## Architecture

The project separates responsibilities:

- ML decides risk probability
- Rule engine detects explicit security indicators
- XAI highlights model feature importance
- RAG retrieves cybersecurity knowledge
- LLM/fallback generates concise human-readable output
- Extension presents the final result in a compact popup UI

## Screenshots

The extension uses a dark security-themed interface with sections for risk score, indicators, evidence, attack type, knowledge, and recommendations.

## Tech Stack

- Python 3.11+
- FastAPI
- Uvicorn
- Pydantic
- scikit-learn
- pandas
- numpy
- joblib
- Python dotenv
- Manifest V3 Chrome extension
- Vanilla JavaScript

## ML Methodology

The primary text model is TF-IDF + logistic regression. The training script creates a reproducible dataset split, fits the model, evaluates the classifier, and saves metrics to JSON. The URL analyzer is an interpretable static risk model rather than a fake real-time blacklist or reputation service.

## Explainable AI

The system shows model feature contributions such as password, immediately, suspended, and verify. These are displayed as a simple bar chart with a human-language explanation describing which features most influenced the decision.

## RAG

The knowledge base includes curated local documents covering phishing basics, credential phishing, spearphishing, malicious URLs, urgency tactics, impersonation, safe verification, best practices, and MITRE ATT&CK.

## Installation

### Quick start

```bash
git clone https://github.com/Disha-53/PhishExplain-AI.git
cd PhishExplain-AI
python -m venv .venv

# Windows
.venv\Scripts\activate

# Linux/macOS
source .venv/bin/activate

pip install -r requirements.txt
python -m uvicorn backend.main:app --reload
```

## Windows Setup

1. Open PowerShell.
2. Go to the project folder.
3. Run the virtual environment commands.
4. Install dependencies with pip.
5. Start the backend with uvicorn.

## Linux/macOS Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python -m uvicorn backend.main:app --reload
```

## Chrome Extension Installation

1. Open Chrome.
2. Visit `chrome://extensions`.
3. Turn on Developer Mode.
4. Click Load unpacked.
5. Select the `extension/` folder.

### Extension permissions

The extension only requests minimal permissions needed to read the active tab and communicate with the local backend:

- `activeTab`
- `scripting`
- `storage`
- `http://127.0.0.1:8000/*`

This avoids broad access such as `<all_urls>` unless a real requirement arises later.

## Usage

1. Start the backend.
2. Load the extension in Chrome.
3. Paste a message or URL into the popup, or highlight text on a page.
4. Click Analyze.
5. Review the resulting risk score, model evidence, indicators, cybersecurity context, and recommendation.

## API

### GET /health

```json
{
  "status": "ok",
  "version": "1.0.0"
}
```

### POST /analyze

Request:

```json
{
  "text": "Your account will be suspended. Verify your password immediately.",
  "url": "http://example-login.com"
}
```

Response:

```json
{
  "label": "LIKELY PHISHING",
  "risk_score": 94,
  "severity": "CRITICAL",
  "attack_type": "Credential Phishing",
  "indicators": ["Urgency", "Credential request"],
  "xai": [{"feature": "password", "impact": 0.21}],
  "url_analysis": {"risk_score": 80, "label": "HIGH", "summary": "Static URL analysis"},
  "knowledge": {"source": "local knowledge base", "results": []},
  "explanation": "This message is considered high risk because it contains urgency and credential-related language.",
  "recommendation": "Do not click the link. Verify the request through the organization's official website."
}
```

## Dataset

This prototype uses a compact local synthetic dataset for reproducible training and demos. For production use, expand this with a larger labelled corpus and better evaluation coverage.

## Evaluation

The training script captures:

- Accuracy
- Precision
- Recall
- F1 score
- ROC-AUC
- Confusion matrix

These metrics are saved to `models/text_metrics.json` after training.

## Limitations

- This is a local prototype, not a production-grade detection service.
- URL analysis is static and explainable rather than using real-time threat intelligence.
- The knowledge base is local and curated rather than a full enterprise corpus.
- The system intentionally avoids over-claiming certainty.

## Privacy

The extension is designed to work locally with a localhost backend. If an external LLM provider is later configured, the user should be explicitly informed that content may be sent to that provider. No secrets are committed to the repository.

## Security

- No API keys are hard-coded
- Use environment variables for optional AI integrations
- Untrusted content is treated as evidence, not instructions
- Request size is limited in the API schema and route logic
- The UI avoids unsafe raw HTML rendering

## Future Scope

- Gmail and Outlook integration
- Microsoft and messaging platform integrations
- Multilingual phishing detection
- Attachment analysis
- Real-time threat intelligence
- Domain reputation services
- Enterprise dashboards

## Team

This project is a prototype for explainable phishing detection and cybersecurity awareness.

## License

This project is licensed under the MIT License.

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
## Explainable AI

The system shows model feature contributions such as password, immediately, suspended, and verify. These are displayed as a simple bar chart with a human-language explanation describing which features most influenced the decision.

## RAG

## Detection Pipeline

- **ML prediction:** text Logistic Regression and, when trained, the URL model.
- **Rule-based indicators:** observable urgency, credential, threat, financial, link, and impersonation patterns.
- **Model-derived XAI:** observed TF-IDF features multiplied by fitted model coefficients.
- **RAG knowledge:** semantically retrieved cybersecurity guidance that never changes the prediction.

Text probability uses `0.0-1.0`; URL and final risk scores use `0-100`.

## ML Methodology

The deployable text baseline is TF-IDF + Logistic Regression trained only from
`data/processed/text/messages.csv`. The training script compares it with a
Linear SVM and writes metrics only after a real dataset is present. The URL
pipeline uses `backend/services/url_features.py` during both training and
inference, excluding webpage-derived features that cannot be reproduced from a
new URL.
git clone https://github.com/Disha-53/PhishExplain-AI.git
cd PhishExplain-AI
python -m venv .venv
## Embedding-Based RAG

Run `python scripts/build_rag_index.py` to chunk the local Markdown documents,
embed them with `all-MiniLM-L6-v2`, and persist a FAISS index plus JSON metadata
under `data/vector_db/`. The backend loads this index at startup and returns
top-k similarity-ranked chunks. If it is absent, the API reports unavailable
status instead of returning invented context.
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
## Dataset Pipeline

Dataset files are never committed. See [DATASETS.md](DATASETS.md) for verified
source status, label mappings, licensing notes, and manual/authenticated
download instructions. Run `python scripts/preprocess_text_data.py` before
`python training/train_text_model.py`. Run the URL preprocessing and training
commands after obtaining PhiUSIIL.
python -m uvicorn backend.main:app --reload
```
# PhishExplain AI

## Overview

PhishExplain AI is a FastAPI phishing-analysis backend with a Chrome extension
and a Streamlit API client. It analyzes message text and URLs while keeping ML
prediction, observable rules, model-derived evidence, and cybersecurity
knowledge clearly separate.

## Architecture and Pipeline

Both clients call the same `GET /health` and `POST /analyze` API.

- **ML prediction:** TF-IDF + Logistic Regression text model and optional URL ML model.
- **Rule evidence:** urgency, threat, credential, financial, link, and impersonation indicators.
- **Model-derived XAI:** observed TF-IDF values multiplied by fitted model coefficients.
- **Embedding RAG:** SentenceTransformer embeddings and FAISS similarity retrieval.
- **Explanation:** deterministic, grounded output that does not require an LLM key.

Text probability uses `0.0-1.0`; URL and final risk scores use `0-100`.

## Installation

```bash
git clone https://github.com/Disha-53/PhishExplain-AI.git
cd PhishExplain-AI
python -m venv .venv
```

Windows: `.venv\Scripts\activate`
Linux/macOS: `source .venv/bin/activate`

```bash
pip install -r requirements.txt
python scripts/verify_setup.py
python scripts/build_rag_index.py
python -m uvicorn backend.main:app --reload
```

Copy `.env.example` to `.env` for local configuration. Never commit `.env` or
credentials.

## Dataset and Training

Dataset files are never committed. See [DATASETS.md](DATASETS.md) for verified
source status, labels, licensing, and authentication/manual download steps.

```bash
python scripts/download_datasets.py nazario
python scripts/preprocess_text_data.py
python training/train_text_model.py
python scripts/download_datasets.py phiusiil
python scripts/preprocess_url_data.py
python training/train_url_model.py
```

Training refuses to run without processed real data. Text compares Logistic
Regression with Linear SVM; URL compares Logistic Regression with Random Forest.
Metrics and metadata are written under `models/` and `reports/` only after an
actual training run.

## RAG

`python scripts/build_rag_index.py` chunks the repository Markdown documents
with 180-word chunks and 30-word overlap, embeds them with the configured
`all-MiniLM-L6-v2` model, and writes `data/vector_db/knowledge.faiss` plus
`knowledge_chunks.json`. The backend retrieves configurable top-k chunks. If no
index exists, it returns an explicit unavailable status and empty results.

## API

`GET /health` returns `{ "status": "ok", "version": "1.0.0" }`.

`POST /analyze` accepts text, URL, or both:

```json
{"text": "Verify your account immediately", "url": "https://example.com/login"}
```

The response includes classification, risk score, severity, attack type,
indicators, URL analysis, XAI evidence, RAG context, explanation, and
recommendation.

## Chrome Extension

Load `extension/` from `chrome://extensions` with Developer Mode enabled. The
popup checks `/health`, supports text-only/URL-only/combined analysis, uses a
10-second request timeout, and safely renders returned content. The API URL
defaults to `http://127.0.0.1:8000`; set `chrome.storage.local.apiBaseUrl` to a
deployed HTTPS backend and add that host to `host_permissions` before packaging.

## Streamlit

Streamlit calls the backend and does not load duplicate ML models:

```powershell
$env:BACKEND_URL="http://127.0.0.1:8000"
streamlit run streamlit_app.py
```

Use `BACKEND_URL` or Streamlit secrets in production.

## Dashboard Frontend

The merged visual dashboard is a static FastAPI client at
`demo/phishing-demo.html`. Start it from the repository root after configuring
the backend CORS origins:

```powershell
$env:CORS_ORIGINS="http://127.0.0.1:5500,http://localhost:5500"
python -m uvicorn backend.main:app --host 127.0.0.1 --port 8000
python -m http.server 5500 --directory demo --bind 127.0.0.1
```

Open `http://127.0.0.1:5500/phishing-demo.html`. The dashboard stores an
optional production backend URL in `localStorage` under
`phishExplainApiUrl`; otherwise it uses `http://127.0.0.1:8000`.

## Configuration and Deployment

Supported settings include `ENVIRONMENT`, `API_HOST`, `API_PORT`/`PORT`,
`CORS_ORIGINS`, `MODEL_DIR`, `KNOWLEDGE_DIR`, `VECTOR_DB_DIR`, `RAG_TOP_K`, and
`RAG_EMBEDDING_MODEL`. Production should provide exact CORS origins and host
model/FAISS artifacts through release storage or a model registry. The service
does not recreate production artifacts from synthetic data.

## Limitations and Security

The repository does not claim real-world accuracy until the documented datasets
are downloaded, processed, trained, and evaluated locally. URL analysis remains
static and has no reputation lookup. The cited AI-generated-phishing GitHub
source currently returns 404 and is not replaced silently. No external LLM is
required. Untrusted text is treated as evidence, secrets are environment-only,
and backend content is rendered with safe DOM APIs in the extension.

## License

MIT. Dataset licenses and terms remain those of their publishers.
- Multilingual phishing detection

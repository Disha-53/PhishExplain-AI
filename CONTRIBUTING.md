# Contributing to PhishExplain AI

Thank you for contributing.

## Development setup

1. Create a virtual environment.
2. Install dependencies with `pip install -r requirements.txt`.
3. Run the backend with `python -m uvicorn backend.main:app --reload`.
4. Load the extension in Chrome from the `extension/` directory.

## Contribution guidelines

- Keep the ML, rule engine, XAI, and RAG layers separate.
- Do not hard-code secrets.
- Prefer small, testable changes.
- Add or update tests for bug fixes.

# Architecture

PhishExplain AI follows a layered design:

1. Browser extension collects text or page context.
2. FastAPI backend validates input and routes the request.
3. ML and rule analyzers compute risk signals.
4. Risk engine combines the signals into a risk score.
5. XAI component explains influential features.
6. RAG retrieves relevant cybersecurity knowledge.
7. LLM or fallback explanation produces a final user-facing recommendation.

The design keeps responsibilities separate so the model is not allowed to silently become a knowledge engine or a final decision maker.

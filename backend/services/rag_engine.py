from __future__ import annotations

import os
from typing import Any


KNOWLEDGE_DIR = os.path.join("knowledge")


class RAGEngine:
    def __init__(self, knowledge_dir: str | None = None):
        self.knowledge_dir = knowledge_dir or KNOWLEDGE_DIR
        self.documents = self._load_documents()

    def _load_documents(self) -> list[dict[str, str]]:
        files = [
            "phishing_basics.md",
            "credential_phishing.md",
            "spearphishing.md",
            "malicious_urls.md",
            "social_engineering.md",
            "urgency_tactics.md",
            "impersonation.md",
            "cybersecurity_best_practices.md",
            "mitre_attack_phishing.md",
        ]
        results: list[dict[str, str]] = []
        for filename in files:
            path = os.path.join(self.knowledge_dir, filename)
            if os.path.exists(path):
                with open(path, "r", encoding="utf-8") as f:
                    content = f.read().strip()
                if content:
                    results.append({"title": filename.replace(".md", "").replace("_", " ").title(), "content": content})
        if not results:
            results.append({
                "title": "Fallback knowledge",
                "content": "Credential phishing attempts to steal account credentials using urgency and trusted-looking links. Verify requests using official channels independently.",
            })
        return results

    def retrieve(self, query: str) -> dict[str, Any]:
        term = (query or "").strip().lower()
        if not term:
            term = "credential phishing urgent login"

        matches: list[dict[str, str]] = []
        for doc in self.documents:
            score = 0
            text = doc["content"].lower()
            for keyword in term.split():
                if keyword in text:
                    score += 1
            if score > 0 or len(matches) == 0:
                matches.append({"title": doc["title"], "content": doc["content"], "score": score})

        if not matches:
            return {"source": "fallback", "results": [{"title": "Fallback knowledge", "content": "Credential phishing attempts to steal account credentials using urgency and trusted-looking links. Verify requests using official channels independently."}]}

        ordered = sorted(matches, key=lambda item: item["score"], reverse=True)[:3]
        return {"source": "local knowledge base", "results": [{"title": item["title"], "content": item["content"]} for item in ordered]}

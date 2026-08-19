from __future__ import annotations

import os

import requests
import streamlit as st
from dotenv import load_dotenv

load_dotenv()
BACKEND_URL = os.getenv("BACKEND_URL", "http://127.0.0.1:8000").rstrip("/")

st.set_page_config(page_title="PhishExplain AI", page_icon="🛡️", layout="centered")
st.title("PhishExplain AI")
st.caption("Explainable phishing analysis through the shared FastAPI backend")

text = st.text_area("Message or email text", height=220)
url = st.text_input("Optional suspicious URL")

if st.button("Analyze", type="primary"):
    if not text.strip() and not url.strip():
        st.warning("Provide message text, a URL, or both.")
    else:
        try:
            response = requests.post(
                f"{BACKEND_URL}/analyze",
                json={"text": text, "url": url},
                timeout=15,
            )
            response.raise_for_status()
            data = response.json()
        except requests.Timeout:
            st.error("The backend request timed out.")
        except requests.RequestException as error:
            st.error(f"The FastAPI backend is unavailable: {error}")
        except ValueError:
            st.error("The backend returned invalid JSON.")
        else:
            st.subheader("Prediction")
            st.metric("Classification", data.get("label", "UNKNOWN"), f"{data.get('risk_score', 0)} / 100")
            st.write(f"Severity: **{data.get('severity', 'UNKNOWN')}**")
            st.write(f"Attack type: **{data.get('attack_type', 'Unknown')}**")

            st.subheader("Rule-based indicators")
            st.write(data.get("indicators") or "No rule indicators returned.")

            st.subheader("URL analysis")
            st.json(data.get("url_analysis", {}))

            st.subheader("Model-derived XAI evidence")
            st.json(data.get("xai", []))

            st.subheader("Retrieved cybersecurity knowledge")
            knowledge = data.get("knowledge", {})
            if knowledge.get("status") == "unavailable":
                st.info("The embedding knowledge index is not available.")
            for item in knowledge.get("results", []):
                st.markdown(f"**{item.get('title', 'Knowledge')}**")
                st.write(item.get("text", item.get("content", "")))

            st.subheader("Explanation")
            st.write(data.get("explanation", ""))
            st.subheader("Recommendation")
            st.write(data.get("recommendation", ""))
"""
Streamlit frontend for the Text Analyzer API.

It reads the backend's URL from the BACKEND_URL environment variable so the
exact same code works locally and on Render without changing any source.

Run locally (after starting the backend on port 8000):
    export BACKEND_URL=http://localhost:8000   # macOS / Linux
    streamlit run app.py
"""

from __future__ import annotations

import os

import requests
import streamlit as st

# Default to localhost so the app "just works" during development.
# On Render, we override this with an env var pointing to the deployed backend.
BACKEND_URL = os.environ.get("BACKEND_URL", "http://localhost:8000")

st.set_page_config(page_title="Text Analyzer", page_icon="🔤", layout="centered")

st.title("🔤 Text Analyzer")
st.caption(f"Backend: `{BACKEND_URL}`")

with st.sidebar:
    st.header("About")
    st.write(
        "This Streamlit app sends text to a **FastAPI** backend. "
        "The backend computes statistics and sends them back as JSON."
    )
    if st.button("Ping backend"):
        try:
            r = requests.get(f"{BACKEND_URL}/health", timeout=10)
            r.raise_for_status()
            st.success(r.json())
        except requests.RequestException as e:
            st.error(f"Could not reach backend: {e}")

text = st.text_area(
    "Paste some text to analyze:",
    height=200,
    placeholder="Type or paste any text...",
)

if st.button("Analyze", type="primary", disabled=not text.strip()):
    with st.spinner("Asking the backend..."):
        try:
            resp = requests.post(
                f"{BACKEND_URL}/analyze",
                json={"text": text},
                timeout=30,  # Render free-tier can be slow to wake from sleep
            )
            resp.raise_for_status()
            data = resp.json()
        except requests.RequestException as e:
            st.error(f"Request failed: {e}")
            st.stop()

    c1, c2, c3 = st.columns(3)
    c1.metric("Words", data["word_count"])
    c2.metric("Characters", data["character_count"])
    c3.metric("Sentences", data["sentence_count"])
    st.metric("Avg word length", data["average_word_length"])

    st.subheader("Most common words")
    if data["top_words"]:
        st.bar_chart({w: c for w, c in data["top_words"]})
    else:
        st.info("Not enough words to compute a ranking.")

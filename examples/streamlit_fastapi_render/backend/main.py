"""
FastAPI backend: a tiny Text Analyzer API.

Endpoints
---------
GET  /          -> sanity-check message + link to docs
GET  /health    -> used by the frontend to verify the backend is up
POST /analyze   -> accepts {"text": "..."} and returns word/char/sentence stats

Run locally
-----------
    uvicorn main:app --reload --port 8000

Then open http://localhost:8000/docs to try it from the interactive UI.
"""

from __future__ import annotations

import re
from collections import Counter

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

app = FastAPI(title="Text Analyzer API", version="1.0.0")

# The Streamlit frontend runs on a DIFFERENT origin (different domain/port),
# so browsers block requests by default. CORS middleware tells the browser
# the backend is happy to be called from anywhere. For a public tutorial API
# this is fine; in production, restrict `allow_origins` to your frontend URL.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


class AnalyzeRequest(BaseModel):
    text: str = Field(..., min_length=1, description="Text to analyze")


class AnalyzeResponse(BaseModel):
    word_count: int
    character_count: int
    sentence_count: int
    average_word_length: float
    top_words: list[tuple[str, int]]


@app.get("/")
def root() -> dict[str, str]:
    return {"message": "Text Analyzer API. See /docs for interactive docs."}


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/analyze", response_model=AnalyzeResponse)
def analyze(req: AnalyzeRequest) -> AnalyzeResponse:
    text = req.text
    words = re.findall(r"\b[\w']+\b", text.lower())
    sentences = [s for s in re.split(r"[.!?]+\s*", text.strip()) if s]

    avg_len = sum(len(w) for w in words) / len(words) if words else 0.0

    return AnalyzeResponse(
        word_count=len(words),
        character_count=len(text),
        sentence_count=len(sentences),
        average_word_length=round(avg_len, 2),
        top_words=Counter(words).most_common(5),
    )

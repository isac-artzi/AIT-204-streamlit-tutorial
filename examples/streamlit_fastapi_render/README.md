# Streamlit + FastAPI — Full-Stack Example

A tiny two-service app to demonstrate a Streamlit frontend talking to a
FastAPI backend. Used by [**RENDER_DEPLOYMENT_GUIDE.md**](../../RENDER_DEPLOYMENT_GUIDE.md).

```
                 ┌───────────────┐  JSON over HTTPS  ┌────────────────┐
   Your browser ─▶  Streamlit app ─────────────────▶  FastAPI backend  │
                 │   (frontend)  │                   │    /analyze      │
                 └───────────────┘                   └────────────────┘
```

The backend analyzes a chunk of text and returns word count, character count,
sentence count, average word length, and the five most common words.

---

## 📁 Layout

```
streamlit_fastapi_render/
├── backend/
│   ├── main.py               # FastAPI app
│   └── requirements.txt
├── frontend/
│   ├── app.py                # Streamlit app
│   └── requirements.txt
├── .gitignore
└── README.md                 # (this file)
```

We keep backend and frontend in **separate folders with their own
`requirements.txt`** because they're deployed as two independent services.
Render (and most PaaS hosts) will treat each folder as its own project.

---

## 🖥 Run It Locally

You need **two terminals** — one for each service.

### Terminal 1 — backend

```bash
cd examples/streamlit_fastapi_render/backend
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

Open <http://localhost:8000/docs> — you'll see FastAPI's auto-generated
interactive API docs. Try the `/analyze` endpoint right from that page.

### Terminal 2 — frontend

```bash
cd examples/streamlit_fastapi_render/frontend
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
streamlit run app.py
```

Streamlit opens at <http://localhost:8501>. Paste some text, click
**Analyze**, and the stats appear.

---

## 🌍 Deploy It (Free) on Render.com

Follow the full walkthrough in
[**RENDER_DEPLOYMENT_GUIDE.md**](../../RENDER_DEPLOYMENT_GUIDE.md). It assumes
no prior cloud experience and walks through the whole flow, from GitHub push
to a working public URL.

---

## 🔧 How the Services Talk

- The frontend reads a `BACKEND_URL` environment variable.
- Locally it defaults to `http://localhost:8000`.
- On Render, you set `BACKEND_URL` to the backend service's public URL (e.g.
  `https://my-analyzer-api.onrender.com`).

Because the URL is read from the environment, **the same code works
unchanged in both places** — that's a pattern you'll reuse on every project.

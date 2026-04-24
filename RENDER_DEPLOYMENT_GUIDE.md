# Deploying a Streamlit + FastAPI App on Render.com

A from-scratch, no-prior-cloud-experience-required guide to shipping a
two-service Python web app to the internet **for free**.

> **Where this fits:** this is **step 5b** of the tutorial — use it when your
> app has a separate backend (API, ML model server, database). If your app is
> a single Streamlit script with no backend, use **[DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md)**
> instead. New here? Start at the [README](README.md).

By the end, you'll have:

- A **FastAPI** backend running at a public `https://…onrender.com` URL
- A **Streamlit** frontend running at another public `https://…onrender.com` URL
- The frontend calling the backend over the internet, just like any real app

**What you need going in:** basic Python (you can read and edit `.py` files)
and basic GitHub (you know what a commit and a push are). You do **not** need
any cloud experience — every cloud concept you need is explained inline.

**Time to complete:** about 45–60 minutes the first time.

---

## Table of Contents

1. [What We're Building (and Why Two Services)](#1-what-were-building-and-why-two-services)
2. [Key Concepts in 3 Minutes](#2-key-concepts-in-3-minutes)
3. [The Code (Frontend + Backend)](#3-the-code-frontend--backend)
4. [Step 1 — Run It Locally](#step-1--run-it-locally)
5. [Step 2 — Push to GitHub](#step-2--push-to-github)
6. [Step 3 — Create a Render Account](#step-3--create-a-render-account)
7. [Step 4 — Deploy the FastAPI Backend](#step-4--deploy-the-fastapi-backend)
8. [Step 5 — Deploy the Streamlit Frontend](#step-5--deploy-the-streamlit-frontend)
9. [Step 6 — Test End-to-End](#step-6--test-end-to-end)
10. [Free-Tier Gotchas](#free-tier-gotchas)
11. [Troubleshooting](#troubleshooting)
12. [Where to Go Next](#where-to-go-next)

---

## 1. What We're Building (and Why Two Services)

```
     ┌───────────────┐  HTTPS + JSON   ┌────────────────┐
     │  Streamlit    │ ──────────────▶ │   FastAPI       │
     │  (frontend)   │                  │   (backend)      │
     │  port 8501    │ ◀────────────── │   port 8000      │
     └───────────────┘                  └────────────────┘
         what the user sees                what does the work
```

**Frontend (Streamlit)** = the web pages, buttons, charts — the thing the
user looks at in the browser.

**Backend (FastAPI)** = a Python HTTP server that exposes JSON endpoints.
It's where the "real" work happens: running an ML model, talking to a
database, calling an external API, doing heavy computation, etc.

### Why split them at all?

For this tutorial's tiny app you don't *have* to — a pure Streamlit app can
do everything in one process. But in the real world you split the two
whenever you have any of these:

- **Expensive work you don't want to re-run** on every Streamlit re-render
  (Streamlit re-runs your whole script on every click).
- **Work you want to share** between a Streamlit UI, a mobile app, a CLI, a
  scheduled job — anything that can speak HTTP.
- **Scaling needs** — you can give the backend more CPU/RAM than the frontend,
  or vice versa, independently.
- **Secrets** — API keys (OpenAI, AWS, databases, etc.) live on the backend so
  the browser never sees them.

So even though we're just analyzing text here, the pattern you'll learn is the
same one used in production AI apps.

---

## 2. Key Concepts in 3 Minutes

You don't need deep networking knowledge, but these five ideas will make the
rest of the guide click.

| Concept | 1-sentence explanation | Why it matters here |
|---|---|---|
| **Web service** | A program that stays running and replies to HTTP requests. | Both our Streamlit app and FastAPI app are web services. |
| **Port** | A number (like 8000 or 8501) your service listens on. | Render sets a `PORT` environment variable and expects you to listen on it. |
| **Environment variable** | A named value read at runtime (e.g., `PORT=10000`). | We use them to inject the backend URL and port without editing code. |
| **Host `0.0.0.0`** | "Listen on every network interface" (not just inside this container). | Without it, Render can't route outside traffic to your app. |
| **CORS** | Browser rule: a page at site A can't call API at site B unless B allows it. | The FastAPI backend must allow the Streamlit frontend's origin. |

That's the whole mental model. Keep it nearby — every tutorial step is just
one of those five ideas in action.

---

## 3. The Code (Frontend + Backend)

Everything below already exists in this repo at
[`examples/streamlit_fastapi_render/`](examples/streamlit_fastapi_render/).
Read through it so you know what's about to deploy.

### Project layout

```
examples/streamlit_fastapi_render/
├── backend/
│   ├── main.py               # FastAPI app
│   └── requirements.txt
├── frontend/
│   ├── app.py                # Streamlit app
│   └── requirements.txt
├── .gitignore
└── README.md
```

### `backend/main.py` — the FastAPI app

```python
from __future__ import annotations

import re
from collections import Counter

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

app = FastAPI(title="Text Analyzer API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],     # tutorial-simple; tighten this in production
    allow_methods=["*"],
    allow_headers=["*"],
)


class AnalyzeRequest(BaseModel):
    text: str = Field(..., min_length=1)


class AnalyzeResponse(BaseModel):
    word_count: int
    character_count: int
    sentence_count: int
    average_word_length: float
    top_words: list[tuple[str, int]]


@app.get("/")
def root():
    return {"message": "Text Analyzer API. See /docs for interactive docs."}


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/analyze", response_model=AnalyzeResponse)
def analyze(req: AnalyzeRequest):
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
```

### `backend/requirements.txt`

```txt
fastapi==0.115.6
uvicorn[standard]==0.32.1
pydantic==2.10.3
```

### `frontend/app.py` — the Streamlit app

```python
import os
import requests
import streamlit as st

BACKEND_URL = os.environ.get("BACKEND_URL", "http://localhost:8000")

st.set_page_config(page_title="Text Analyzer", page_icon="🔤", layout="centered")
st.title("🔤 Text Analyzer")
st.caption(f"Backend: `{BACKEND_URL}`")

text = st.text_area("Paste some text to analyze:", height=200)

if st.button("Analyze", type="primary", disabled=not text.strip()):
    with st.spinner("Asking the backend..."):
        resp = requests.post(
            f"{BACKEND_URL}/analyze",
            json={"text": text},
            timeout=30,
        )
        resp.raise_for_status()
        data = resp.json()

    c1, c2, c3 = st.columns(3)
    c1.metric("Words", data["word_count"])
    c2.metric("Characters", data["character_count"])
    c3.metric("Sentences", data["sentence_count"])
    st.metric("Avg word length", data["average_word_length"])

    st.subheader("Most common words")
    st.bar_chart({w: c for w, c in data["top_words"]})
```

### `frontend/requirements.txt`

```txt
streamlit==1.40.0
requests==2.32.3
```

**The one line that makes this work in both places:**

```python
BACKEND_URL = os.environ.get("BACKEND_URL", "http://localhost:8000")
```

Locally, `BACKEND_URL` is unset so we fall back to localhost. On Render,
we'll set `BACKEND_URL` to the backend's public URL. Same code, two
environments.

---

## Step 1 — Run It Locally

Always make it work locally before touching the cloud. If it doesn't work on
your laptop, it definitely won't work on Render — and Render logs are harder
to read than your own terminal.

### Install Python 3.11+ if you don't have it

```bash
python3 --version
```

If this prints 3.11 or higher, you're set. Otherwise install from
[python.org](https://www.python.org/downloads/) or use your OS package manager.

### Open two terminals

**Terminal 1 — start the backend:**

```bash
cd examples/streamlit_fastapi_render/backend
python3 -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

Visit <http://localhost:8000/docs>. You should see FastAPI's interactive
Swagger UI — try the `POST /analyze` button right there with some sample text.

> **Why `uvicorn`?** It's the HTTP server that actually runs your FastAPI app.
> FastAPI is just a framework; you need a server to serve it. `uvicorn` is
> the standard choice.

**Terminal 2 — start the frontend:**

```bash
cd examples/streamlit_fastapi_render/frontend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

Streamlit opens at <http://localhost:8501>. Paste some text, click Analyze,
and see the backend's response rendered as metrics and a bar chart.

✅ **If that works, you're ready to deploy.** If it doesn't, fix it now —
don't move on.

---

## Step 2 — Push to GitHub

Render deploys straight from GitHub. It watches your repo and redeploys
every time you push. That means your next move is to get this code into a
GitHub repo you own.

### If the code is already in a repo you own

Just `git push` and skip to Step 3.

### If you're starting from the course repo

You have two options:

**Option A — fork the course repo** (simplest, if your instructor allows it):

1. Click **Fork** in the top right of the GitHub page.
2. On Render, you'll point at your fork.

**Option B — create a new repo just for this project:**

```bash
# From the folder ABOVE Streamlit-tutorial, or anywhere convenient:
cp -R "Streamlit-tutorial/examples/streamlit_fastapi_render" ~/my-fullstack-app
cd ~/my-fullstack-app
git init
git add .
git commit -m "Initial commit: Streamlit + FastAPI starter"
```

Then on [github.com](https://github.com) click **+ → New repository**, name
it (for example) `my-fullstack-app`, leave it empty (no README), and run the
commands GitHub shows you. They look like:

```bash
git remote add origin https://github.com/YOUR_USERNAME/my-fullstack-app.git
git branch -M main
git push -u origin main
```

Refresh the repo page on GitHub — your files should be there.

> **Keep the repo public** for this tutorial. Render can deploy from private
> repos too, but you need to grant extra permissions we're skipping here.

---

## Step 3 — Create a Render Account

1. Go to **<https://render.com>**.
2. Click **Get Started** → **Sign in with GitHub**.
3. Authorize Render to read your repositories.
4. When asked, grant access to the repo you just pushed (or "All repositories"
   if you prefer — you can narrow this later).

No credit card is required for the free tier.

---

## Step 4 — Deploy the FastAPI Backend

We deploy the backend **first** because the frontend needs its URL.

### 4.1 Create a new Web Service

From the Render dashboard:

1. Click **+ New** → **Web Service**.
2. Pick the repository you just connected.
3. Click **Connect**.

### 4.2 Fill out the form

Render shows a long settings form. Here's what to enter — leave anything
not listed at its default.

| Field | Value | Why |
|---|---|---|
| **Name** | `my-analyzer-api` (anything you like) | Becomes part of your URL: `my-analyzer-api.onrender.com` |
| **Region** | Pick the one closest to you | Lower latency |
| **Branch** | `main` | Which branch to deploy |
| **Root Directory** | `examples/streamlit_fastapi_render/backend` (or just `backend` if your repo is the example folder) | Tells Render "cd into here before building" |
| **Runtime** | `Python 3` | Auto-detected from `requirements.txt` |
| **Build Command** | `pip install -r requirements.txt` | Install deps |
| **Start Command** | `uvicorn main:app --host 0.0.0.0 --port $PORT` | Run the app |
| **Instance Type** | **Free** | $0/month |

**Two critical details** in the start command:

- `--host 0.0.0.0` — listen on every interface so Render can route traffic
  to you. The default `127.0.0.1` only accepts connections from inside the
  container and would make your app unreachable.
- `--port $PORT` — Render picks a random port and passes it to your process
  via the `PORT` environment variable. Your app **must** listen on that
  exact port, not a hard-coded `8000`.

### 4.3 Click "Deploy Web Service"

Render starts building. You'll see a live log:

```
==> Cloning from https://github.com/...
==> Using Python version 3.11.x
==> Running 'pip install -r requirements.txt'
==> Running 'uvicorn main:app --host 0.0.0.0 --port $PORT'
INFO:     Uvicorn running on http://0.0.0.0:10000
INFO:     Application startup complete.
==> Your service is live 🎉
```

The first build takes **3–5 minutes**. After that, pushes to `main` redeploy
automatically in under a minute.

### 4.4 Verify the backend is alive

Copy the URL at the top of the page — something like
`https://my-analyzer-api.onrender.com`. Open it in your browser:

```json
{"message": "Text Analyzer API. See /docs for interactive docs."}
```

Then open `https://my-analyzer-api.onrender.com/docs` and try
`POST /analyze` with some sample text. If JSON comes back, the backend is
working. ✅

**Save this URL.** You'll paste it into the frontend config in the next step.

---

## Step 5 — Deploy the Streamlit Frontend

### 5.1 Create a second Web Service

Back on the Render dashboard:

1. Click **+ New** → **Web Service**.
2. Pick the **same** GitHub repo.
3. Click **Connect**.

### 5.2 Fill out the form

| Field | Value |
|---|---|
| **Name** | `my-analyzer-ui` |
| **Region** | Same region you picked for the backend |
| **Branch** | `main` |
| **Root Directory** | `examples/streamlit_fastapi_render/frontend` (or `frontend`) |
| **Runtime** | `Python 3` |
| **Build Command** | `pip install -r requirements.txt` |
| **Start Command** | `streamlit run app.py --server.port $PORT --server.address 0.0.0.0 --server.headless true --server.enableCORS false --server.enableXsrfProtection false` |
| **Instance Type** | **Free** |

The start-command flags matter:

- `--server.port $PORT` — same reason as the backend.
- `--server.address 0.0.0.0` — same reason as the backend.
- `--server.headless true` — don't try to open a browser on the server.
- `--server.enableCORS false --server.enableXsrfProtection false` — Streamlit's
  own anti-CSRF checks can reject requests when running behind Render's proxy.
  Disabling them is fine for this tutorial; for a production app you'd look
  at Streamlit's deployment docs for tighter settings.

### 5.3 Add the `BACKEND_URL` environment variable

**Before clicking Deploy**, scroll down to **Environment Variables** and
click **Add Environment Variable**:

| Key | Value |
|---|---|
| `BACKEND_URL` | `https://my-analyzer-api.onrender.com` *(your backend URL from Step 4.4)* |

This is the whole point of the `os.environ.get("BACKEND_URL", ...)` line in
the frontend code — Render injects this value at runtime, and the Streamlit
app sends requests to the right place without a single code change.

> ⚠️ **No trailing slash**, and it must start with `https://`. A common
> first-time mistake.

### 5.4 Click "Deploy Web Service"

Wait for it to build (another 3–5 minutes).

When it's live, open the frontend URL (e.g.
`https://my-analyzer-ui.onrender.com`). You should see your Streamlit app.
Paste some text and click **Analyze**. The metrics should appear.

---

## Step 6 — Test End-to-End

Once both services are green on Render:

1. **Open the frontend URL** in your browser. The Streamlit app loads.
2. **Click "Analyze" with sample text.** The frontend sends the text to the
   backend; the backend computes stats; the frontend renders them. You just
   watched a real client/server web app do its thing.
3. **Push a change.** Edit `frontend/app.py` locally (change the title
   emoji, say), commit, `git push`. Watch Render auto-redeploy in the
   dashboard. Refresh the frontend URL — your change is live.

Share the URL. It's on the internet, so yes, your friends can open it from
their phones.

---

## Free-Tier Gotchas

These don't break the tutorial, but they *will* surprise you if nobody
mentions them.

### 1. Services "sleep" after 15 minutes of inactivity

When a free service gets no traffic for 15 minutes, Render spins the
container down. The **next** request has to wait ~30–60 seconds while Render
boots it back up. This is why the frontend uses `timeout=30` on its request.

**Implication for the tutorial:** the *first* click after a period of
inactivity is slow. Subsequent clicks are fast.

**If you need always-on:** Render has a paid "Starter" tier (~$7/month per
service) that never sleeps. Don't upgrade for coursework.

### 2. Monthly instance hours

Render free tier gives a pool of instance-hours per month (check the current
number on their pricing page — it has changed over time). Two sleepy
services usually fit comfortably.

### 3. Cold-starts for the backend affect the frontend

If the frontend request to a sleeping backend times out, Streamlit will show
a red error. Click **Analyze** again — by then the backend is awake.

### 4. Ephemeral filesystem

Anything you write to disk on a Render service is **lost** when the service
restarts. If you need to save data between requests, use a database (Render
offers managed Postgres; or use Supabase, Neon, etc.). For this text-stats
demo we don't store anything, so we don't care.

👉 For a from-scratch walkthrough — including free Supabase Postgres and the
`DATABASE_URL` env-var pattern that drops straight into this tutorial's
backend — see **[DATABASE_GUIDE.md](DATABASE_GUIDE.md)**.

### 5. Public URL format

Your URLs look like `https://<service-name>-<random>.onrender.com`. If you
rename a service, the old URL breaks and any client pointing at it must
update.

---

## Troubleshooting

### "Build failed: no module named 'fastapi'"

Your `requirements.txt` wasn't found. Check the **Root Directory** field on
the service — Render must `cd` into the folder that contains your
`requirements.txt`.

### Backend is up but `/docs` returns 404

You're probably hitting the frontend service URL by mistake. Copy the URL
from the **backend** service in the Render dashboard.

### Frontend shows "Could not reach backend"

Three things to check, in order:

1. Is the backend service **live** (green dot) in the Render dashboard?
2. Is the `BACKEND_URL` env var on the **frontend** service exactly equal to
   the backend's public URL, with `https://` and no trailing slash?
3. Did you wait ~60 seconds for a cold-start? Try again.

### Frontend log: "Port scan timeout reached"

Render tests your service by connecting to `$PORT`. If it can't, it kills
the deploy. You probably forgot `--host 0.0.0.0` or `--server.address 0.0.0.0`
in the start command, or you hard-coded the port.

### Streamlit app loads but `st.button` never triggers anything

Almost always caused by Streamlit's CSRF/CORS protections behind the proxy.
Make sure the start command includes both `--server.enableCORS false` and
`--server.enableXsrfProtection false`.

### "CORS" error in the browser console when clicking Analyze

The backend is rejecting the frontend's origin. Check that
`CORSMiddleware` is installed in `backend/main.py` and `allow_origins`
includes `"*"` (or your frontend's exact URL).

### Changes aren't appearing after `git push`

- Make sure you pushed to the **branch Render is watching** (default `main`).
- Check the **Events** tab on the service in Render — you should see a new
  deploy triggered by your commit.

---

## Where to Go Next

You now know how to:

- Split a Python app into a frontend and a backend
- Run both services locally in separate processes
- Deploy each to Render as its own web service
- Wire them together with an environment variable
- Debug the most common deployment failures

Natural next steps:

1. **Swap the backend for something real.** Hook it up to an LLM (OpenAI,
   Anthropic), an ML model you've trained, a database query, or a web
   scraper. The frontend doesn't need to change — only the contract.
2. **Store state.** Add a Render Postgres database and persist the analyses.
3. **Harden CORS.** Replace `allow_origins=["*"]` with your frontend's exact
   URL.
4. **Secure the backend.** Add an API key header the frontend sends, and
   validate it on the backend. Put the key in an environment variable (never
   in code).
5. **Observability.** Add `print(...)` or `logging` in the backend — every
   line shows up in Render's live logs, which is how you debug real traffic.

### Reference

- **Render Python docs**: <https://render.com/docs/deploy-fastapi>
- **Render Streamlit docs**: <https://render.com/docs/deploy-streamlit>
- **FastAPI docs**: <https://fastapi.tiangolo.com/>
- **Streamlit docs**: <https://docs.streamlit.io/>

---

🎉 **You just deployed a two-service Python web app to the internet.** That's
a real skill — you'll use the same pattern for every AI/ML app you ship from
now on.

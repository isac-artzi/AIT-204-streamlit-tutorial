# Databases for Streamlit Apps — SQLite + Supabase Postgres

A from-scratch guide to giving your Streamlit app somewhere to store data.

> **Where this fits:** this is **step 6** of the tutorial. If you haven't
> already, work through the [README](README.md) and try the basic
> [examples](examples/). New to the tutorial? Start at the README.

By the end of this guide you'll know:

- Why you need a database (and when you don't)
- How to use **SQLite in three modes** — read-only, session-scoped, persistent
- Why a plain SQLite file is **not enough** on free cloud tiers
- How to provision a free **Postgres database on Supabase** and connect to it
  from Streamlit with one environment variable

All the code shown here is in
[`examples/database_demo/`](examples/database_demo/).

---

## Table of Contents

1. [Why a Database at All?](#1-why-a-database-at-all)
2. [The Four Patterns in One Table](#2-the-four-patterns-in-one-table)
3. [SQLite Mode 1 — Read-Only (Bundled Data)](#3-sqlite-mode-1--read-only-bundled-data)
4. [SQLite Mode 2 — Session-Scoped Writes](#4-sqlite-mode-2--session-scoped-writes)
5. [SQLite Mode 3 — Persistent Writes (Local)](#5-sqlite-mode-3--persistent-writes-local)
6. [Why SQLite Alone Fails in the Cloud](#6-why-sqlite-alone-fails-in-the-cloud)
7. [Supabase Postgres — Free Tier Setup](#7-supabase-postgres--free-tier-setup)
8. [Connecting Streamlit to Supabase](#8-connecting-streamlit-to-supabase)
9. [Secrets, Deployment, and CI Hygiene](#9-secrets-deployment-and-ci-hygiene)
10. [Common Errors](#10-common-errors)
11. [Where to Go Next](#11-where-to-go-next)

---

## 1. Why a Database at All?

Streamlit apps re-run your script on every interaction. Anything you store
in a plain Python variable vanishes — there's no place for it to live
between clicks. You have three ways around that:

| Tool | Lives as long as | Shared between users | Good for |
|------|------------------|----------------------|----------|
| `st.session_state` | one browser tab | No | Per-user UI state (current step, selected tab, form inputs) |
| A file / SQLite DB | the server process | Yes (shared!) | Demos, shipped datasets, caches |
| A managed database | forever | Yes, with proper auth | Any real data you don't want to lose |

If you can keep something in `st.session_state`, do it — it's simpler.
Reach for a database when you need **persistence across restarts**,
**queries** (filter, sort, aggregate), or **multiple users** seeing the
same data.

---

## 2. The Four Patterns in One Table

| Pattern | How it's implemented | Writable? | Survives restart? | Survives cloud redeploy? |
|--------|-----------------------|-----------|-------------------|--------------------------|
| SQLite read-only | `file:books.db?mode=ro` (URI) | ❌ | N/A | ✅ (bundled in repo) |
| SQLite session-scoped | tempfile or `:memory:` | ✅ | ❌ | ❌ |
| SQLite persistent (local) | plain file path | ✅ | ✅ locally | ❌ on free tiers |
| Postgres (Supabase) | managed service over TLS | ✅ | ✅ | ✅ |

Remember one rule: **free-tier cloud filesystems are ephemeral.** Anything
you write *as a file* on Render free or Streamlit Community Cloud is wiped
on every redeploy, cold start, or platform restart. Only the database
service survives.

---

## 3. SQLite Mode 1 — Read-Only (Bundled Data)

**Use when:** you want to ship a fixed dataset alongside your app —
reference tables, a sample dataset for a demo, lookup values. Users can
query it; nobody can corrupt it.

**How it works:** SQLite supports a URI syntax that opens a connection in
read-only mode. Every `INSERT`/`UPDATE`/`DELETE` raises
`sqlite3.OperationalError` before anything touches the file.

```python
import sqlite3

conn = sqlite3.connect("file:books.db?mode=ro", uri=True, check_same_thread=False)

# Reads work:
rows = conn.execute("SELECT title FROM books WHERE rating >= ?", (4.5,)).fetchall()

# Writes are rejected:
conn.execute("INSERT INTO books (title) VALUES ('x')")
# -> sqlite3.OperationalError: attempt to write a readonly database
```

**Shipping the `.db` file.** Generate it once locally (the
`seed_data.py` script in the example folder does this) and commit the
resulting `books.db` alongside your `.py` file. For larger datasets, use
[Git LFS](https://git-lfs.com) or download the file at startup from object
storage — but for tutorials and small reference data, committing is fine.

> The bundled `.gitignore` in `examples/database_demo/` excludes `*.db` by
> default, assuming you *don't* want to commit it. For the read-only
> example specifically, either remove `*.db` from `.gitignore` and commit
> the seed, or have the `seed_data.py` script run as part of deploy.

**Full example:** [`examples/database_demo/01_sqlite_readonly.py`](examples/database_demo/01_sqlite_readonly.py).

---

## 4. SQLite Mode 2 — Session-Scoped Writes

**Use when:** you want users to write data that should disappear on
restart — a class demo, a throwaway analysis scratchpad, data you
deliberately don't want to retain.

**How it works:** create the database in the OS temp directory (or as
`:memory:`). Cache the connection with `@st.cache_resource` so every
Streamlit rerun reuses the same DB within the server's lifetime.

```python
import sqlite3, tempfile
from pathlib import Path
import streamlit as st

@st.cache_resource
def get_conn():
    tmp = Path(tempfile.gettempdir()) / "streamlit_session.db"
    if tmp.exists():
        tmp.unlink()                  # fresh DB on each server boot
    conn = sqlite3.connect(tmp, check_same_thread=False)
    conn.execute("CREATE TABLE items (id INTEGER PRIMARY KEY, name TEXT)")
    return conn
```

**The big gotcha:** every visitor to your Streamlit server sees the same
database. There's no per-user isolation — if user A adds an item, user B
sees it. That's fine for a solo demo; it's a privacy bug in anything real.
For per-user state, use `st.session_state` (small data) or a real database
+ auth (anything bigger).

**Full example:** [`examples/database_demo/02_sqlite_session.py`](examples/database_demo/02_sqlite_session.py).

---

## 5. SQLite Mode 3 — Persistent Writes (Local)

**Use when:** you're running the app on your laptop and want data to
survive restarts. The simplest possible persistence story.

```python
import sqlite3

@st.cache_resource
def get_conn():
    conn = sqlite3.connect("notes.db", check_same_thread=False)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS notes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            body TEXT NOT NULL,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)
    return conn
```

Stop the app, restart it, and your notes are still there. Ship it to a
teammate with the `.db` file and they get your data too.

**Full example:** [`examples/database_demo/03_sqlite_persistent.py`](examples/database_demo/03_sqlite_persistent.py).

---

## 6. Why SQLite Alone Fails in the Cloud

Here's the gotcha every first-time deployer hits.

You run Mode 3 locally. It works perfectly. You push it to Streamlit
Community Cloud or Render free tier. Data saves. You're thrilled.

Then you push a tiny fix to `app.py`. The platform redeploys — and every
note your users wrote is gone.

Why? Free-tier hosts use **ephemeral filesystems**: every container starts
from the image you built, with no carry-over from the last run. Writes to
`./notes.db` happen *inside* the container and are thrown away with it.

**You have three ways out:**

1. **Paid persistent disk.** Render offers persistent disks on its paid
   tiers. Works fine, costs money, SQLite stays as-is.
2. **An external SQLite-as-a-service** like
   [Turso](https://turso.tech) or [LiteFS](https://fly.io/docs/litefs/).
   Good if you're already committed to SQLite.
3. **A managed Postgres** like Supabase, Neon, or Render Postgres.
   Battle-tested, a generous free tier, and the pattern transfers to every
   real job you'll ever do.

We'll go with option 3.

---

## 7. Supabase Postgres — Free Tier Setup

[Supabase](https://supabase.com) gives you a free Postgres database (plus
auth, object storage, and more — we'll only use the DB) with:

- **500 MB** database storage
- **2 free projects**
- **Automatic pausing** after ~1 week of inactivity (one click to resume)
- No credit card required

### 7.1 Create a Supabase account

1. Go to [supabase.com](https://supabase.com) → **Start your project** →
   sign in with GitHub.
2. Create a new organization when prompted (your personal name is fine).

### 7.2 Create a project

1. Click **+ New project**.
2. Fill in:
   - **Name** — anything memorable, e.g. `streamlit-notes`.
   - **Database password** — **SAVE THIS**. You'll need it in the connection
     string. Use a password manager; don't reuse any existing password.
   - **Region** — pick the one closest to where your app will be deployed.
3. Click **Create new project**. Provisioning takes about 1 minute.

### 7.3 Copy the connection string

Once the project is ready:

1. Click the **Connect** button in the top bar (or go to
   **Project Settings → Database**).
2. You'll see several connection strings. Copy the **Transaction pooler**
   URL (port `6543`) — it looks like:

   ```
   postgresql://postgres.abcdefghijklm:[YOUR-PASSWORD]@aws-0-us-east-1.pooler.supabase.com:6543/postgres
   ```

3. Replace `[YOUR-PASSWORD]` with the DB password you set in step 7.2.

> **Why the pooler?** Short-lived processes (Streamlit reruns, Render free
> tier cold-starts, serverless functions) open and close connections
> frequently. The pooler is designed for that. The *direct* URL on port
> `5432` is better suited to long-lived, high-throughput apps.

### 7.4 Create a table (optional — the code will do it for you)

Our example runs `CREATE TABLE IF NOT EXISTS` on startup, so you don't
have to touch the Supabase SQL editor. But if you want to poke around:

1. In the Supabase dashboard, open the **SQL Editor**.
2. Paste:

   ```sql
   CREATE TABLE IF NOT EXISTS notes (
       id         SERIAL PRIMARY KEY,
       body       TEXT NOT NULL,
       created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
   );
   ```

3. Click **Run**. You can also explore rows under **Table Editor → notes**.

---

## 8. Connecting Streamlit to Supabase

### 8.1 Install the Postgres driver

In the `examples/database_demo/` virtual environment:

```bash
pip install "psycopg[binary]==3.2.3"
```

`psycopg` is the modern Python Postgres driver. The `[binary]` extra ships
precompiled wheels so you don't need to install Postgres headers on your
machine.

### 8.2 Put the URL in Streamlit secrets

Create `.streamlit/secrets.toml` (**this file is gitignored**):

```toml
[supabase]
DATABASE_URL = "postgresql://postgres.abcdefghijklm:YOUR-PASSWORD@aws-0-us-east-1.pooler.supabase.com:6543/postgres"
```

A template (`secrets.toml.example`) ships in the example folder — just
copy it and edit.

### 8.3 The connect-and-query code

```python
import os, psycopg, streamlit as st

def get_db_url() -> str:
    # Streamlit Community Cloud reads .streamlit/secrets.toml; elsewhere we
    # fall back to a plain environment variable (Render, Docker, CI, etc.).
    try:
        return st.secrets["supabase"]["DATABASE_URL"]
    except Exception:
        return os.environ["DATABASE_URL"]

@st.cache_resource
def get_conn():
    return psycopg.connect(get_db_url(), sslmode="require", autocommit=True)

conn = get_conn()

# Write (always parameterize — %s, never f-strings)
with conn.cursor() as cur:
    cur.execute("INSERT INTO notes (body) VALUES (%s)", ("Hello Postgres",))

# Read
with conn.cursor() as cur:
    cur.execute("SELECT id, body, created_at FROM notes ORDER BY id DESC")
    rows = cur.fetchall()
```

Three details that matter:

- **`sslmode="require"`** — Supabase rejects non-TLS connections.
- **`autocommit=True`** — keeps the example simple; each statement commits
  immediately. For transactional writes, drop it and call `conn.commit()`
  explicitly.
- **`@st.cache_resource`** — one connection per Streamlit server, reused
  across every rerun. Without this you'd open a new connection on every
  button click.

**Full example:** [`examples/database_demo/04_postgres_supabase.py`](examples/database_demo/04_postgres_supabase.py).

---

## 9. Secrets, Deployment, and CI Hygiene

You'll use the same pattern every time you ship a DB-backed app.

### Local development

`.streamlit/secrets.toml` (gitignored). Never commit a real password.

### Streamlit Community Cloud

In your app dashboard → **⋮ → Settings → Secrets**, paste the same TOML
block. Restart the app. `st.secrets["supabase"]["DATABASE_URL"]` resolves
to the value you set.

### Render.com

Render has no `st.secrets` concept — it exposes environment variables.
The `get_db_url()` helper above falls back to `os.environ["DATABASE_URL"]`
for exactly this case.

In the Render dashboard for your web service:

1. **Environment → Add Environment Variable**
2. **Key** = `DATABASE_URL`, **Value** = your pooler URL
3. Save — Render restarts the service automatically

### What NOT to do

- ❌ Paste the DB URL into `app.py` and commit it.
- ❌ Print secrets to logs (`print(DATABASE_URL)`, `st.write(DATABASE_URL)`).
- ❌ Include secrets in error messages you surface to the UI.
- ❌ Leave the default `postgres` role's password weak — Supabase lets you
  rotate it from **Settings → Database** in one click. Do that immediately
  if you suspect a leak.

### If you *do* leak a password

1. Rotate it in the Supabase dashboard (**Settings → Database → Reset database
   password**).
2. Update every place you stored the old URL — `secrets.toml`, Render env
   vars, Streamlit Cloud secrets, CI.
3. Check your Git history with `git log -p` for the leaked value; if it's
   in a public repo, assume it's compromised even after you remove it.

---

## 10. Common Errors

### `sqlite3.OperationalError: attempt to write a readonly database`

You're running the read-only example and clicked the "try to insert"
button — **this is the expected behavior.** That's the guarantee SQLite's
URI read-only mode gives you.

### `sqlite3.OperationalError: unable to open database file`

The path is wrong or the parent directory doesn't exist. Use absolute
paths via `pathlib.Path(__file__).parent / "notes.db"` instead of relative
paths — your working directory isn't always what you think.

### `psycopg.OperationalError: connection failed: FATAL: Tenant or user not found`

Your pooler URL is missing the `.project-ref` suffix on the username.
Supabase poolers need `postgres.abcdefghijklm` (project ref after the
dot), not just `postgres`. Recopy from the dashboard.

### `psycopg.OperationalError: SSL connection has been closed unexpectedly`

Often a Supabase project that's been paused for inactivity. Open the
dashboard — it will prompt you to resume.

### `psycopg.errors.UndefinedTable: relation "notes" does not exist`

The `CREATE TABLE IF NOT EXISTS` step didn't run. Check you called
`ensure_schema(conn)` before any query; or create the table manually in
the Supabase SQL Editor.

### My notes vanish every time I redeploy on Streamlit Cloud / Render free

You're still using the SQLite persistent example (#3). Switch to the
Postgres example (#4) — this is exactly what Section 6 warned about.

---

## 11. Where to Go Next

- **Migrations.** `CREATE TABLE IF NOT EXISTS` is fine for a tutorial.
  For real schemas, learn [Alembic](https://alembic.sqlalchemy.org/) or
  use `supabase db push`.
- **ORM vs raw SQL.** This tutorial uses raw SQL because it's the clearest
  teaching tool and transfers to any language. Once you've shipped a few
  DB-backed apps, try [SQLAlchemy](https://www.sqlalchemy.org/) or
  [SQLModel](https://sqlmodel.tiangolo.com/) for larger projects.
- **Auth.** Supabase has built-in auth (email, OAuth, magic link). Wire it
  up so each user sees only their own rows — that's the foundation of
  every multi-user app.
- **Backups.** Supabase takes daily backups on paid plans. On the free
  tier, export important data periodically (`pg_dump`).
- **Pair with the other guides.** The
  [`streamlit_fastapi_render`](examples/streamlit_fastapi_render/) example
  becomes *much* more interesting once its FastAPI backend talks to
  Postgres. The `DATABASE_URL` env-var pattern drops straight in.

---

**Previous:** [RENDER_DEPLOYMENT_GUIDE.md](RENDER_DEPLOYMENT_GUIDE.md)
(deploy to the cloud) ·
**Index:** [README.md](README.md)

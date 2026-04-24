# Database Examples — SQLite (3 modes) + Supabase Postgres

Four small Streamlit apps, each showing one way to handle data persistence:

| # | File | What it shows |
|---|------|---------------|
| 1 | [`01_sqlite_readonly.py`](01_sqlite_readonly.py) | Ship a pre-seeded SQLite file; app can read but **cannot** write |
| 2 | [`02_sqlite_session.py`](02_sqlite_session.py) | SQLite in a temp file — writes persist within a server lifetime, reset on restart |
| 3 | [`03_sqlite_persistent.py`](03_sqlite_persistent.py) | SQLite on a real file path — persists locally; does NOT persist on free cloud tiers |
| 4 | [`04_postgres_supabase.py`](04_postgres_supabase.py) | Managed Postgres on Supabase — the right answer for persistent cloud data |

For the full conceptual walkthrough (why each mode exists, when to use which,
how to sign up for Supabase), read **[DATABASE_GUIDE.md](../../DATABASE_GUIDE.md)**.

---

## 🛠 Setup

```bash
cd examples/database_demo
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

---

## 🏃 Run each example

### 1. Read-only SQLite

One-time seed of the sample dataset, then launch:

```bash
python seed_data.py
streamlit run 01_sqlite_readonly.py
```

Click **Try to INSERT a fake book** — SQLite rejects the write with a visible
`OperationalError`. That's the guarantee.

### 2. Session-scoped SQLite

```bash
streamlit run 02_sqlite_session.py
```

Add a book, then change a character in the file and save. Streamlit reloads
the script, the tmpfile is recreated, and your list is gone. That's the
"write during session" behavior.

### 3. Persistent SQLite (local)

```bash
streamlit run 03_sqlite_persistent.py
```

Save a note, stop the app with `Ctrl+C`, restart — the note is still there.
Now try deploying this same app to Streamlit Community Cloud or Render free
tier: the next redeploy wipes `notes.db`. That's the ephemeral-filesystem
lesson.

### 4. Supabase Postgres

Follow the short setup in the docstring at the top of
[`04_postgres_supabase.py`](04_postgres_supabase.py), or the step-by-step in
[DATABASE_GUIDE.md](../../DATABASE_GUIDE.md), to:

1. Create a free Supabase project.
2. Copy the pooler connection string.
3. Put it in `.streamlit/secrets.toml` (a template is at
   `.streamlit/secrets.toml.example`).

Then:

```bash
streamlit run 04_postgres_supabase.py
```

Save a note, restart the app, redeploy it — the note survives because it's
in Postgres, not on the ephemeral container filesystem.

---

## 📁 Layout

```
database_demo/
├── README.md                      # this file
├── requirements.txt
├── seed_data.py                   # creates books.db for example 1
├── 01_sqlite_readonly.py
├── 02_sqlite_session.py
├── 03_sqlite_persistent.py
├── 04_postgres_supabase.py
├── .gitignore                     # ignores *.db and secrets.toml
└── .streamlit/
    └── secrets.toml.example       # copy to secrets.toml and edit
```

---

## 🔐 Security reminders

- **Never commit** `books.db`, `notes.db`, or `.streamlit/secrets.toml` to a
  public repo. The bundled `.gitignore` handles this.
- **Always use parameterized queries.** SQLite: `?` placeholders. Postgres:
  `%s` placeholders. Never build SQL with f-strings.
- **Don't paste DB URLs in chat, in screenshots, or in public GitHub issues.**
  Rotate the password immediately if you do — Supabase lets you reset it from
  the dashboard in one click.

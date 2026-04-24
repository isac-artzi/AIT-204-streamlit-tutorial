"""
Postgres on Supabase (free tier).

Same "notes" schema as example 03, but persisted to a managed Postgres
database. Data survives code pushes, cold starts, and platform restarts.

Setup (one-time)
----------------
1. Sign up at https://supabase.com and create a free project.
2. Wait ~1 minute for it to provision.
3. In the project → Project Settings → Database → Connection string,
   copy the URI (starts with `postgresql://`). Replace `[YOUR-PASSWORD]`
   with the DB password you chose when creating the project.

   💡 For deployed apps on Render / Streamlit Cloud, prefer the **Transaction
   pooler** URL (port `6543`) over the direct URL (port `5432`). The pooler
   plays nicely with short-lived containers.

4. Put the URL in `.streamlit/secrets.toml` (which is gitignored):

       [supabase]
       DATABASE_URL = "postgresql://postgres.xxxxxxx:YOUR-PASSWORD@aws-0-us-east-1.pooler.supabase.com:6543/postgres"

   Or export it as an environment variable:

       export DATABASE_URL="postgresql://..."

5. Run:

       pip install -r requirements.txt
       streamlit run 04_postgres_supabase.py
"""

from __future__ import annotations

import os

import pandas as pd
import psycopg
import streamlit as st

st.set_page_config(page_title="Notes (Supabase)", page_icon="🗃️")
st.title("🗃️ Notes — persistent on Supabase Postgres")


def get_db_url() -> str:
    """
    Look up the DB URL in two places, in order:

    1. Streamlit secrets — `[supabase] DATABASE_URL` in .streamlit/secrets.toml
       (or the `Secrets` field on Streamlit Community Cloud).
    2. The `DATABASE_URL` environment variable (how Render / most hosts inject
       configuration).
    """
    try:
        return st.secrets["supabase"]["DATABASE_URL"]
    except Exception:
        pass  # fall through to env var

    url = os.environ.get("DATABASE_URL")
    if not url:
        st.error(
            "No database URL configured. Set `[supabase] DATABASE_URL` in "
            "`.streamlit/secrets.toml` or the `DATABASE_URL` environment "
            "variable. See the docstring at the top of this file."
        )
        st.stop()
    return url


@st.cache_resource
def get_conn() -> psycopg.Connection:
    # `sslmode=require` is standard for Supabase. `autocommit=True` keeps
    # the example simple — every statement commits immediately.
    return psycopg.connect(get_db_url(), sslmode="require", autocommit=True)


def ensure_schema(conn: psycopg.Connection) -> None:
    with conn.cursor() as cur:
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS notes (
                id         SERIAL PRIMARY KEY,
                body       TEXT NOT NULL,
                created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
            )
            """
        )


conn = get_conn()
ensure_schema(conn)

# --- Write -------------------------------------------------------------------
body = st.text_area("Write a note", height=100)
if st.button("Save", type="primary", disabled=not body.strip()):
    with conn.cursor() as cur:
        # Always use parameterized queries (%s) — NEVER f-strings — to avoid
        # SQL injection.
        cur.execute("INSERT INTO notes (body) VALUES (%s)", (body.strip(),))
    st.rerun()

# --- Read --------------------------------------------------------------------
with conn.cursor() as cur:
    cur.execute(
        "SELECT id, body, created_at FROM notes ORDER BY id DESC LIMIT 200"
    )
    rows = cur.fetchall()

df = pd.DataFrame(rows, columns=["id", "body", "created_at"])

st.subheader(f"Your notes ({len(df)})")
if df.empty:
    st.info("No notes yet. Save one above — then redeploy or restart and watch it survive.")
else:
    st.dataframe(df, use_container_width=True, hide_index=True)

# --- Tips --------------------------------------------------------------------
with st.expander("ℹ️ Production notes"):
    st.markdown(
        """
- **Connection pooler vs direct URL.** Supabase exposes two connection
  strings — use the *pooler* (port `6543`) for serverless-style hosts
  (Render free, AWS Lambda, etc.) where processes spin up and down. Use
  the *direct* URL (port `5432`) for long-lived servers doing many queries
  per second.
- **Parameterize queries.** `cur.execute("... WHERE x = %s", (val,))` is
  safe; building SQL with f-strings is a SQL-injection bug.
- **Schema migrations.** `CREATE TABLE IF NOT EXISTS` is fine for tutorials.
  For real apps, use a migration tool (Alembic, or `supabase db push`).
- **Secrets hygiene.** Never commit `secrets.toml` or paste the DB URL in
  code. The `.gitignore` in this folder already excludes it.
        """
    )

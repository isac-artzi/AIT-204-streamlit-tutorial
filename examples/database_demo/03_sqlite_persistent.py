"""
SQLite — mode 3: persistent write (local).

Writes go to a normal file on disk. Data survives Streamlit reloads and full
process restarts — ON YOUR LAPTOP.

⚠️ Cloud reality check
-----------------------
Most free-tier hosts (Streamlit Community Cloud, Render free, Heroku-style
platforms) give every new container a clean filesystem. Any file you write
at runtime — including this `notes.db` — disappears on every:

  • Code push / redeploy
  • Cold-start after idle sleep
  • Platform maintenance restart

So this pattern is great locally but *not* how you persist data in the
cloud. When you need real cloud persistence, graduate to a managed database:
see `04_postgres_supabase.py`.

Run:
    streamlit run 03_sqlite_persistent.py
"""

from __future__ import annotations

import sqlite3
from pathlib import Path

import pandas as pd
import streamlit as st

DB_PATH = Path(__file__).parent / "notes.db"

st.set_page_config(page_title="Notes (persistent)", page_icon="📝")
st.title("📝 Notes — persistent locally")
st.caption(f"Writing to `{DB_PATH.name}` — survives local restarts.")


@st.cache_resource
def get_conn() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS notes (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            body       TEXT NOT NULL,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
        """
    )
    return conn


conn = get_conn()

# --- Write -------------------------------------------------------------------
body = st.text_area(
    "Write a note", height=100, placeholder="Anything you want to remember..."
)
if st.button("Save", type="primary", disabled=not body.strip()):
    conn.execute("INSERT INTO notes (body) VALUES (?)", (body.strip(),))
    conn.commit()
    st.rerun()

# --- Read --------------------------------------------------------------------
df = pd.read_sql_query(
    "SELECT id, body, created_at FROM notes ORDER BY id DESC LIMIT 200", conn
)
st.subheader(f"Your notes ({len(df)})")
if df.empty:
    st.info("No notes yet — write one above, hit Save, and restart the app to see it persist.")
else:
    st.dataframe(df, use_container_width=True, hide_index=True)

# --- Cloud warning -----------------------------------------------------------
with st.expander("⚠️ Why this will NOT persist on Streamlit Cloud / Render free tier"):
    st.markdown(
        """
Those hosts give each deployment a clean filesystem, and spin containers
down after inactivity. Every restart wipes `notes.db`.

**For persistent cloud data, move to a managed database** — see
`04_postgres_supabase.py` in this folder, or read the full walkthrough in
[`DATABASE_GUIDE.md`](../../DATABASE_GUIDE.md).
        """
    )

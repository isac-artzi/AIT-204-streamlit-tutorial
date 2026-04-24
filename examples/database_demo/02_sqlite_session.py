"""
SQLite — mode 2: session-scoped / ephemeral writes.

The database is a fresh file in the OS temp dir, created the first time the
app loads. Writes succeed and persist across reruns and widget interactions,
but the file is wiped whenever the Streamlit server process restarts (after
a code change, a redeploy, or a cloud cold-start).

Use cases:
  • Demos where data should reset on each deploy
  • Throwaway state you don't want leaking into production data
  • Tests

⚠️ One caveat: all visitors to the same Streamlit server share this database.
There is NO per-user isolation. For per-user state, use `st.session_state`
(small data) or a real database with authentication (real apps).

Run:
    streamlit run 02_sqlite_session.py
"""

from __future__ import annotations

import sqlite3
import tempfile
from pathlib import Path

import pandas as pd
import streamlit as st

st.set_page_config(page_title="Reading list (session)", page_icon="🗒️")
st.title("🗒️ Reading list — session-scoped")
st.caption(
    "Writes succeed but vanish on server restart. "
    "Try adding a book, then edit this file and save — Streamlit reloads "
    "the script and the list is gone."
)


@st.cache_resource
def get_conn() -> sqlite3.Connection:
    tmp = Path(tempfile.gettempdir()) / "streamlit_session_books.db"
    # Start fresh each time this cache is (re)built.
    if tmp.exists():
        tmp.unlink()
    conn = sqlite3.connect(tmp, check_same_thread=False)
    conn.execute(
        """
        CREATE TABLE books (
            id       INTEGER PRIMARY KEY AUTOINCREMENT,
            title    TEXT NOT NULL,
            author   TEXT,
            added_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
        """
    )
    return conn


conn = get_conn()

# --- Add form ----------------------------------------------------------------
with st.form("add_book", clear_on_submit=True):
    c1, c2 = st.columns(2)
    title = c1.text_input("Title")
    author = c2.text_input("Author")
    submitted = st.form_submit_button("Add book", type="primary")
    if submitted and title.strip():
        conn.execute(
            "INSERT INTO books (title, author) VALUES (?, ?)",
            (title.strip(), author.strip() or None),
        )
        conn.commit()
        st.success(f"Added: {title}")

# --- List --------------------------------------------------------------------
df = pd.read_sql_query(
    "SELECT id, title, author, added_at FROM books ORDER BY id DESC", conn
)

st.subheader(f"Your list ({len(df)} book{'s' if len(df) != 1 else ''})")
if df.empty:
    st.info("No books yet — add one above.")
else:
    st.dataframe(df, use_container_width=True, hide_index=True)

    to_delete = st.selectbox("Delete a book (by id):", [None] + df["id"].tolist())
    if to_delete is not None and st.button("Delete", type="secondary"):
        conn.execute("DELETE FROM books WHERE id = ?", (to_delete,))
        conn.commit()
        st.rerun()

st.divider()
st.caption(
    "💡 Every visitor sees the same list — this pattern is fine for class "
    "demos, not for anything real."
)

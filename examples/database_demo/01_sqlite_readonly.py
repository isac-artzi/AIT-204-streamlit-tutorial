"""
SQLite — mode 1: read-only.

Ships a pre-populated `books.db` and opens it with `?mode=ro`, which asks
SQLite to refuse ALL writes at the filesystem level. Perfect for:

  • Reference / lookup data shipped alongside your app
  • Sample datasets in tutorials
  • Safe demos you want anyone to be able to query but nobody to mutate

Before running, seed the DB once:
    python seed_data.py

Then:
    streamlit run 01_sqlite_readonly.py
"""

from __future__ import annotations

import sqlite3
from pathlib import Path

import pandas as pd
import streamlit as st

DB_PATH = Path(__file__).parent / "books.db"

st.set_page_config(page_title="Books Catalog (read-only)", page_icon="📚")
st.title("📚 Books Catalog")
st.caption("SQLite opened in **read-only** mode — writes will be rejected.")

if not DB_PATH.exists():
    st.error("`books.db` not found. Run `python seed_data.py` in this folder first.")
    st.stop()


@st.cache_resource
def get_conn() -> sqlite3.Connection:
    # The URI form + `mode=ro` gives you a real read-only connection.
    # Any INSERT / UPDATE / DELETE raises sqlite3.OperationalError.
    return sqlite3.connect(
        f"file:{DB_PATH}?mode=ro",
        uri=True,
        check_same_thread=False,
    )


conn = get_conn()

# --- Filters -----------------------------------------------------------------
st.sidebar.header("Filters")
genres = [g for (g,) in conn.execute("SELECT DISTINCT genre FROM books ORDER BY genre")]
selected_genre = st.sidebar.selectbox("Genre", ["All"] + genres)
min_rating = st.sidebar.slider("Min rating", 0.0, 5.0, 4.0, 0.1)

# --- Parameterized query (no string interpolation!) --------------------------
sql = "SELECT id, title, author, year, genre, rating FROM books WHERE rating >= ?"
params: list = [min_rating]
if selected_genre != "All":
    sql += " AND genre = ?"
    params.append(selected_genre)
sql += " ORDER BY rating DESC, year DESC"

df = pd.read_sql_query(sql, conn, params=params)

st.metric("Books matching filters", len(df))
st.dataframe(df, use_container_width=True, hide_index=True)

# --- Demonstrate the read-only guarantee ------------------------------------
st.divider()
st.subheader("🔒 Proof: writes are blocked")
st.write("Click the button — SQLite will raise an error instead of writing.")

if st.button("Try to INSERT a fake book"):
    try:
        conn.execute(
            "INSERT INTO books (title, author, year, genre, rating) "
            "VALUES (?, ?, ?, ?, ?)",
            ("Fake Book", "Nobody", 2020, "Test", 1.0),
        )
        conn.commit()
        st.error("⚠️ Uh oh — the write succeeded. That shouldn't happen.")
    except sqlite3.OperationalError as e:
        st.success(f"Write blocked as expected:\n\n`{e}`")

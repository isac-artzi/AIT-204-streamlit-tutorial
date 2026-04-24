"""
Seed the local `books.db` used by `01_sqlite_readonly.py`.

Run this ONCE before launching the read-only example:
    python seed_data.py
"""

from __future__ import annotations

import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent / "books.db"

BOOKS: list[tuple[str, str, int, str, float]] = [
    ("The Pragmatic Programmer", "Hunt & Thomas", 1999, "Software", 4.8),
    ("Clean Code", "Robert C. Martin", 2008, "Software", 4.5),
    ("Designing Data-Intensive Applications", "Martin Kleppmann", 2017, "Software", 4.9),
    ("Deep Learning", "Goodfellow, Bengio & Courville", 2016, "AI/ML", 4.5),
    ("The Hundred-Page Machine Learning Book", "Andriy Burkov", 2019, "AI/ML", 4.4),
    ("Hands-On Machine Learning", "Aurélien Géron", 2022, "AI/ML", 4.8),
    ("Sapiens", "Yuval Noah Harari", 2011, "History", 4.5),
    ("Thinking, Fast and Slow", "Daniel Kahneman", 2011, "Psychology", 4.4),
    ("Atomic Habits", "James Clear", 2018, "Self-Help", 4.7),
    ("The Hitchhiker's Guide to the Galaxy", "Douglas Adams", 1979, "Fiction", 4.6),
    ("The Da Vinci Code", "Dan Brown", 2003, "Fiction", 3.9),
    ("1984", "George Orwell", 1949, "Fiction", 4.7),
]


def main() -> None:
    if DB_PATH.exists():
        DB_PATH.unlink()

    conn = sqlite3.connect(DB_PATH)
    conn.execute(
        """
        CREATE TABLE books (
            id     INTEGER PRIMARY KEY AUTOINCREMENT,
            title  TEXT NOT NULL,
            author TEXT NOT NULL,
            year   INTEGER NOT NULL,
            genre  TEXT NOT NULL,
            rating REAL NOT NULL
        )
        """
    )
    conn.executemany(
        "INSERT INTO books (title, author, year, genre, rating) VALUES (?, ?, ?, ?, ?)",
        BOOKS,
    )
    conn.commit()
    conn.close()
    print(f"Seeded {DB_PATH} with {len(BOOKS)} books.")


if __name__ == "__main__":
    main()

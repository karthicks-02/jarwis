import sqlite3
from datetime import datetime, timezone
from typing import Optional
import config

CREATE_TABLES = """
CREATE TABLE IF NOT EXISTS conversations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TEXT NOT NULL,
    user_text TEXT NOT NULL,
    jarwis_reply TEXT NOT NULL,
    language TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS facts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    fact TEXT NOT NULL,
    created_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS user_profile (
    key TEXT PRIMARY KEY,
    value TEXT NOT NULL,
    updated_at TEXT NOT NULL
);
"""

class Memory:
    def __init__(self, db_path: str = config.DB_PATH):
        import os
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self.conn.executescript(CREATE_TABLES)
        self.conn.commit()

    def save_fact(self, fact: str) -> None:
        self.conn.execute(
            "INSERT INTO facts (fact, created_at) VALUES (?, ?)",
            (fact, datetime.now(timezone.utc).isoformat())
        )
        self.conn.commit()

    def get_top_facts(self, query: str, k: int = 3) -> list[str]:
        rows = self.conn.execute("SELECT fact FROM facts").fetchall()
        query_words = set(query.lower().split())
        scored = []
        for row in rows:
            fact_words = set(row["fact"].lower().split())
            score = len(query_words & fact_words)
            if score > 0:
                scored.append((score, row["fact"]))
        scored.sort(reverse=True)
        return [f for _, f in scored[:k]]

    def save_conversation(self, user_text: str, jarwis_reply: str, language: str) -> None:
        self.conn.execute(
            "INSERT INTO conversations (timestamp, user_text, jarwis_reply, language) VALUES (?, ?, ?, ?)",
            (datetime.now(timezone.utc).isoformat(), user_text, jarwis_reply, language)
        )
        self.conn.commit()

    def get_recent_conversations(self, limit: int = 5) -> list[dict]:
        rows = self.conn.execute(
            "SELECT * FROM conversations ORDER BY id DESC LIMIT ?", (limit,)
        ).fetchall()
        return [dict(r) for r in rows]

    def set_profile(self, key: str, value: str) -> None:
        self.conn.execute(
            "INSERT OR REPLACE INTO user_profile (key, value, updated_at) VALUES (?, ?, ?)",
            (key, value, datetime.now(timezone.utc).isoformat())
        )
        self.conn.commit()

    def get_profile(self, key: str) -> Optional[str]:
        row = self.conn.execute(
            "SELECT value FROM user_profile WHERE key = ?", (key,)
        ).fetchone()
        return row["value"] if row else None

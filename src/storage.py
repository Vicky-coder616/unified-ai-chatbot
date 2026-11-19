"""SQLite persistence for a single local demo conversation."""

import sqlite3
from pathlib import Path


def connect(path="chat_history.db"):
    connection = sqlite3.connect(str(Path(path)))
    connection.execute("""CREATE TABLE IF NOT EXISTS messages (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        role TEXT NOT NULL CHECK(role IN ('user','assistant')),
        content TEXT NOT NULL,
        created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
    )""")
    connection.commit()
    return connection


def save(connection, role, content):
    connection.execute(
        "INSERT INTO messages(role,content) VALUES (?,?)", (role, content)
    )
    connection.commit()


def recent(connection, limit=15):
    if not isinstance(limit, int) or not 1 <= limit <= 100:
        raise ValueError("History limit must be 1–100")
    rows = connection.execute(
        "SELECT role,content FROM (SELECT id,role,content FROM messages ORDER BY id DESC LIMIT ?) ORDER BY id",
        (limit,),
    ).fetchall()
    return [{"role": role, "content": content} for role, content in rows]


def search(connection, keyword, limit=10):
    if not keyword.strip() or not isinstance(limit, int) or not 1 <= limit <= 100:
        raise ValueError("Provide a keyword and a limit of 1–100")
    escaped = keyword.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")
    return connection.execute(
        "SELECT role,content FROM messages WHERE content LIKE ? ESCAPE '\\' ORDER BY id DESC LIMIT ?",
        (f"%{escaped}%", limit),
    ).fetchall()


def save_turn(connection, question, answer):
    with connection:
        connection.executemany(
            "INSERT INTO messages(role,content) VALUES (?,?)",
            [("user", question), ("assistant", answer)],
        )

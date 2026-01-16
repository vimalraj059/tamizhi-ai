import sqlite3
import os
from contextlib import contextmanager

# --------------------------------------------------
# FIXED DATABASE PATH (VERY IMPORTANT)
# --------------------------------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_NAME = os.path.join(BASE_DIR, "tamizhi.db")

# --------------------------------------------------
# DB CONNECTION (SAFE CONTEXT MANAGER)
# --------------------------------------------------
@contextmanager
def get_db():
    conn = sqlite3.connect(DB_NAME, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()

# --------------------------------------------------
# CREATE TABLES
# --------------------------------------------------
def create_tables():
    with get_db() as conn:
        cursor = conn.cursor()

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS chats (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user TEXT NOT NULL,
            title TEXT DEFAULT 'New Chat',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            chat_id INTEGER NOT NULL,
            role TEXT NOT NULL,
            content TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (chat_id) REFERENCES chats(id)
        )
        """)

        conn.commit()

# --------------------------------------------------
# CHAT OPERATIONS
# --------------------------------------------------
def create_chat(user):
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO chats (user, title) VALUES (?, ?)",
            (user, "New Chat")
        )
        conn.commit()
        return cursor.lastrowid

def get_user_chats(user):
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT id, title, created_at
            FROM chats
            WHERE user=?
            ORDER BY created_at DESC
            """,
            (user,)
        )
        return cursor.fetchall()

def get_chat(chat_id):
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM chats WHERE id=?",
            (chat_id,)
        )
        return cursor.fetchone()

# 🔥 NEW: UPDATE CHAT TITLE (AUTO TITLE SUPPORT)
def update_chat_title(chat_id, title):
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE chats SET title=? WHERE id=?",
            (title, chat_id)
        )
        conn.commit()

# --------------------------------------------------
# MESSAGE OPERATIONS
# --------------------------------------------------
def save_message(chat_id, role, content):
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO messages (chat_id, role, content) VALUES (?, ?, ?)",
            (chat_id, role, content)
        )
        conn.commit()

def get_messages(chat_id):
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT role, content, created_at
            FROM messages
            WHERE chat_id=?
            ORDER BY created_at ASC
            """,
            (chat_id,)
        )
        return cursor.fetchall()

import sqlite3

DB_NAME = "chat_history.db"

def get_conn():
    return sqlite3.connect(DB_NAME, check_same_thread=False)

def init_db():
    conn = get_conn()
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS chats (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT,
            role TEXT,
            message TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)

    conn.commit()
    conn.close()

def save_message(username, role, message):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO chats (username, role, message) VALUES (?, ?, ?)",
        (username, role, message)
    )
    conn.commit()
    conn.close()

def get_history(username):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        "SELECT role, message FROM chats WHERE username=? ORDER BY id",
        (username,)
    )
    rows = cur.fetchall()
    conn.close()
    return rows

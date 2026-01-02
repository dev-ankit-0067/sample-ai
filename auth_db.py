"""SQLite-backed auth helper module.

Provides: init_db(), migrate_from_json(), create_user(), authenticate_user(), list_users().
"""
from pathlib import Path
import sqlite3
import json
import bcrypt
from typing import Optional, Dict, List

DB_PATH = Path(__file__).parent / "users.db"
USERS_FILE = Path(__file__).parent / "users.json"


def _get_conn():
    return sqlite3.connect(DB_PATH)


def init_db() -> None:
    """Create the users table if it doesn't exist."""
    with _get_conn() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                username TEXT PRIMARY KEY,
                password_hash TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        conn.commit()


def migrate_from_json() -> int:
    """Migrate users from `users.json` into the SQLite DB.

    Returns the number of users migrated.
    """
    if not USERS_FILE.exists():
        return 0
    try:
        data = json.loads(USERS_FILE.read_text())
    except Exception:
        return 0

    if not isinstance(data, dict):
        return 0

    migrated = 0
    init_db()
    with _get_conn() as conn:
        for username, hashed in data.items():
            try:
                cur = conn.execute("SELECT 1 FROM users WHERE username=?", (username,))
                if cur.fetchone() is None:
                    conn.execute(
                        "INSERT INTO users (username, password_hash) VALUES (?, ?)",
                        (username, hashed),
                    )
                    migrated += 1
            except Exception:
                continue
        conn.commit()
    return migrated


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


def check_password(password: str, hashed: str) -> bool:
    try:
        return bcrypt.checkpw(password.encode(), hashed.encode())
    except Exception:
        return False


def create_user(username: str, password: str) -> (bool, str):
    """Create a new user. Returns (ok, message)."""
    init_db()
    hashed = hash_password(password)
    try:
        with _get_conn() as conn:
            conn.execute(
                "INSERT INTO users (username, password_hash) VALUES (?, ?)",
                (username, hashed),
            )
            conn.commit()
        return True, "User created successfully"
    except sqlite3.IntegrityError:
        return False, "User already exists"
    except Exception as e:
        return False, f"Error creating user: {e}"


def authenticate_user(username: str, password: str) -> bool:
    """Return True if credentials are valid."""
    init_db()
    try:
        with _get_conn() as conn:
            cur = conn.execute("SELECT password_hash FROM users WHERE username=?", (username,))
            row = cur.fetchone()
            if not row:
                return False
            return check_password(password, row[0])
    except Exception:
        return False


def list_users() -> List[str]:
    init_db()
    with _get_conn() as conn:
        cur = conn.execute("SELECT username FROM users ORDER BY created_at DESC")
        return [r[0] for r in cur.fetchall()]


__all__ = [
    "init_db",
    "migrate_from_json",
    "create_user",
    "authenticate_user",
    "list_users",
]

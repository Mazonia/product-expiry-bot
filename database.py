"""
SQLite Database Manager for tracked bills, medicines, and groceries.
"""

import sqlite3
from datetime import datetime, date, timedelta
from typing import List, Dict, Any, Optional
import config


def get_connection():
    conn = sqlite3.connect(config.DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    with get_connection() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                title TEXT NOT NULL,
                category TEXT NOT NULL,
                expiry_date TEXT NOT NULL,
                amount REAL DEFAULT 0.0,
                notes TEXT DEFAULT '',
                is_resolved INTEGER DEFAULT 0,
                last_notified TEXT DEFAULT '',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()


def add_item(user_id: int, title: str, category: str, expiry_date: str, amount: float = 0.0, notes: str = "") -> int:
    with get_connection() as conn:
        cursor = conn.execute(
            """INSERT INTO items (user_id, title, category, expiry_date, amount, notes)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (user_id, title, category.title(), expiry_date, amount, notes)
        )
        conn.commit()
        return cursor.lastrowid


def get_active_items(user_id: int, category: Optional[str] = None) -> List[Dict[str, Any]]:
    with get_connection() as conn:
        if category:
            cursor = conn.execute(
                """SELECT * FROM items WHERE user_id = ? AND is_resolved = 0 AND LOWER(category) = LOWER(?)
                   ORDER BY expiry_date ASC""",
                (user_id, category)
            )
        else:
            cursor = conn.execute(
                """SELECT * FROM items WHERE user_id = ? AND is_resolved = 0
                   ORDER BY expiry_date ASC""",
                (user_id,)
            )
        return [dict(row) for row in cursor.fetchall()]


def get_items_due_between(days_from_now: int) -> List[Dict[str, Any]]:
    """Get items expiring on or before target days."""
    target_date = (date.today() + timedelta(days=days_from_now)).isoformat()
    today_str = date.today().isoformat()
    with get_connection() as conn:
        cursor = conn.execute(
            """SELECT * FROM items 
               WHERE is_resolved = 0 AND expiry_date <= ?
               ORDER BY expiry_date ASC""",
            (target_date,)
        )
        return [dict(row) for row in cursor.fetchall()]


def mark_resolved(item_id: int) -> bool:
    with get_connection() as conn:
        cursor = conn.execute("UPDATE items SET is_resolved = 1 WHERE id = ?", (item_id,))
        conn.commit()
        return cursor.rowcount > 0


def delete_item(item_id: int) -> bool:
    with get_connection() as conn:
        cursor = conn.execute("DELETE FROM items WHERE id = ?", (item_id,))
        conn.commit()
        return cursor.rowcount > 0


init_db()

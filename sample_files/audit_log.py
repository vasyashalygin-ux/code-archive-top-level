"""Аудит-лог для отслеживания действий пользователей."""
import sqlite3
import json
from datetime import datetime
from typing import List, Dict, Any, Optional


class AuditLog:
    """Система аудита для записи и хранения действий пользователей."""

    def __init__(self, db_path: str):
        """Инициализация аудит-лога с базой данных."""
        self.db_path = db_path
        self._init_table()

    def _init_table(self) -> None:
        """Создать таблицу аудита, если она не существует."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS audit_log (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    action TEXT NOT NULL,
                    resource TEXT,
                    details TEXT,
                    ip_address TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            """)

    def log_action(self, user_id: int, action: str, resource: str = None,
                   details: Dict = None, ip_address: str = None) -> int:
        """Записать действие пользователя в аудит-лог."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                "INSERT INTO audit_log (user_id, action, resource, details, ip_address) VALUES (?, ?, ?, ?, ?)",
                (user_id, action, resource, json.dumps(details) if details else None, ip_address)
            )
            return cursor.lastrowid

    def get_user_actions(self, user_id: int, limit: int = 50) -> List[Dict[str, Any]]:
        """Получить историю действий пользователя."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            rows = conn.execute(
                "SELECT * FROM audit_log WHERE user_id = ? ORDER BY created_at DESC LIMIT ?",
                (user_id, limit)
            ).fetchall()
            return [dict(r) for r in rows]

    def get_actions_by_type(self, action: str) -> List[Dict[str, Any]]:
        """Получить все действия определённого типа из аудит-лога."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            rows = conn.execute(
                "SELECT * FROM audit_log WHERE action = ? ORDER BY created_at DESC",
                (action,)
            ).fetchall()
            return [dict(r) for r in rows]

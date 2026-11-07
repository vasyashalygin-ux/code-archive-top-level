"""Репозиторий для работы с данными пользователей."""
import sqlite3
from typing import Optional, List, Dict, Any


class UserRepository:
    """Репозиторий пользователей с поддержкой базовых операций."""

    def __init__(self, db_path: str):
        """Инициализация репозитория с путём к базе данных."""
        self.db_path = db_path
        self._init_schema()

    def _init_schema(self) -> None:
        """Создать таблицу пользователей, если она не существует."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    email TEXT UNIQUE NOT NULL,
                    password_hash TEXT NOT NULL,
                    is_active INTEGER DEFAULT 1,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            """)

    def find_by_id(self, user_id: int) -> Optional[Dict]:
        """Найти пользователя по уникальному идентификатору."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            row = conn.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
            return dict(row) if row else None

    def find_by_username(self, username: str) -> Optional[Dict]:
        """Найти пользователя по имени пользователя."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            row = conn.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()
            return dict(row) if row else None

    def create(self, username: str, email: str, password_hash: str) -> int:
        """Создать нового пользователя и вернуть его идентификатор."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                "INSERT INTO users (username, email, password_hash) VALUES (?, ?, ?)",
                (username, email, password_hash)
            )
            return cursor.lastrowid

    def update_email(self, user_id: int, new_email: str) -> bool:
        """Обновить email-адрес пользователя."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("UPDATE users SET email = ? WHERE id = ?", (new_email, user_id))
            return True

    def deactivate(self, user_id: int) -> bool:
        """Деактивировать учётную запись пользователя."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("UPDATE users SET is_active = 0 WHERE id = ?", (user_id,))
            return True

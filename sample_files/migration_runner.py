"""Система миграций базы данных."""
import sqlite3
import os
from typing import List
from pathlib import Path


class MigrationRunner:
    """Исполнитель миграций схемы базы данных."""

    def __init__(self, db_path: str, migrations_dir: str):
        """Инициализация с путями к БД и директории с миграциями."""
        self.db_path = db_path
        self.migrations_dir = Path(migrations_dir)

    def _ensure_migrations_table(self, conn: sqlite3.Connection) -> None:
        """Создать таблицу для отслеживания применённых миграций."""
        conn.execute("""
            CREATE TABLE IF NOT EXISTS _migrations (
                id INTEGER PRIMARY KEY,
                name TEXT UNIQUE NOT NULL,
                applied_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)

    def get_applied_migrations(self, conn: sqlite3.Connection) -> List[str]:
        """Получить список уже применённых миграций."""
        rows = conn.execute("SELECT name FROM _migrations ORDER BY id").fetchall()
        return [row[0] for row in rows]

    def run_pending(self) -> int:
        """Применить все ожидающие миграции и вернуть их количество."""
        sql_files = sorted(self.migrations_dir.glob("*.sql"))
        count = 0
        with sqlite3.connect(self.db_path) as conn:
            self._ensure_migrations_table(conn)
            applied = set(self.get_applied_migrations(conn))
            for migration_file in sql_files:
                if migration_file.name not in applied:
                    sql = migration_file.read_text()
                    conn.executescript(sql)
                    conn.execute("INSERT INTO _migrations (name) VALUES (?)", (migration_file.name,))
                    count += 1
        return count

    def rollback_last(self) -> bool:
        """Откатить последнюю применённую миграцию."""
        with sqlite3.connect(self.db_path) as conn:
            last = conn.execute("SELECT name FROM _migrations ORDER BY id DESC LIMIT 1").fetchone()
            if not last:
                return False
            conn.execute("DELETE FROM _migrations WHERE name = ?", (last[0],))
            return True

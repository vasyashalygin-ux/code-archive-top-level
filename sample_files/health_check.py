"""Эндпоинты и утилиты для проверки работоспособности сервиса."""
import time
import sqlite3
from typing import Dict, Any


class HealthChecker:
    """Компонент проверки состояния зависимостей сервиса."""

    def __init__(self, db_path: str):
        """Инициализация с путём к базе данных."""
        self.db_path = db_path
        self._start_time = time.time()

    def check_database(self) -> Dict[str, Any]:
        """Проверить доступность базы данных SQLite."""
        try:
            with sqlite3.connect(self.db_path, timeout=2) as conn:
                conn.execute("SELECT 1")
            return {"status": "ok", "latency_ms": 0}
        except Exception as e:
            return {"status": "error", "error": str(e)}

    def get_uptime(self) -> float:
        """Получить время работы сервиса в секундах."""
        return time.time() - self._start_time

    def full_check(self) -> Dict[str, Any]:
        """Выполнить полную проверку всех компонентов сервиса."""
        db_status = self.check_database()
        return {
            "status": "healthy" if db_status["status"] == "ok" else "degraded",
            "uptime_seconds": self.get_uptime(),
            "components": {
                "database": db_status
            }
        }

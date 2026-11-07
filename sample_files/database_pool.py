"""Пул соединений с базой данных."""
import sqlite3
import threading
from typing import Optional
from contextlib import contextmanager
from queue import Queue, Empty


class ConnectionPool:
    """Пул соединений SQLite для многопоточного использования."""

    def __init__(self, db_path: str, pool_size: int = 5):
        """Инициализация пула соединений с заданным размером."""
        self.db_path = db_path
        self.pool_size = pool_size
        self._pool: Queue = Queue(maxsize=pool_size)
        self._lock = threading.Lock()
        for _ in range(pool_size):
            conn = sqlite3.connect(db_path, check_same_thread=False)
            conn.row_factory = sqlite3.Row
            self._pool.put(conn)

    @contextmanager
    def get_connection(self, timeout: float = 5.0):
        """Получить соединение из пула в контексте менеджера."""
        conn = None
        try:
            conn = self._pool.get(timeout=timeout)
            yield conn
        except Empty:
            raise TimeoutError("Нет доступных соединений в пуле")
        finally:
            if conn:
                self._pool.put(conn)

    def close_all(self) -> None:
        """Закрыть все соединения в пуле."""
        while not self._pool.empty():
            conn = self._pool.get_nowait()
            conn.close()

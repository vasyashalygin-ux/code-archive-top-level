"""Репозиторий для работы с продуктами в базе данных."""
import sqlite3
from typing import Optional, List


class ProductRepository:
    """Репозиторий товаров с поддержкой CRUD-операций."""

    def __init__(self, db_path: str):
        """Инициализация репозитория с путём к базе данных."""
        self.db_path = db_path

    def find_by_id(self, product_id: int) -> Optional[dict]:
        """Найти товар по идентификатору."""
        with sqlite3.connect(self.db_path) as conn:
            row = conn.execute(
                "SELECT * FROM products WHERE id = ?", (product_id,)
            ).fetchone()
            return dict(row) if row else None

    def find_all(self, limit: int = 100, offset: int = 0) -> List[dict]:
        """Получить список всех товаров с пагинацией."""
        with sqlite3.connect(self.db_path) as conn:
            rows = conn.execute(
                "SELECT * FROM products LIMIT ? OFFSET ?", (limit, offset)
            ).fetchall()
            return [dict(r) for r in rows]

    def save(self, product: dict) -> int:
        """Сохранить новый товар и вернуть его идентификатор."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                "INSERT INTO products (name, price, stock) VALUES (?, ?, ?)",
                (product["name"], product["price"], product["stock"])
            )
            return cursor.lastrowid

    def delete(self, product_id: int) -> bool:
        """Удалить товар по идентификатору."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("DELETE FROM products WHERE id = ?", (product_id,))
            return True

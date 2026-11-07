"""Утилиты для кэширования данных."""
import time
from typing import Any, Optional
from functools import wraps


class InMemoryCache:
    """Простой кэш в памяти с поддержкой TTL."""

    def __init__(self):
        """Инициализация пустого кэша."""
        self._store = {}

    def get(self, key: str) -> Optional[Any]:
        """Получить значение из кэша по ключу."""
        entry = self._store.get(key)
        if not entry:
            return None
        value, expires_at = entry
        if expires_at and time.time() > expires_at:
            del self._store[key]
            return None
        return value

    def set(self, key: str, value: Any, ttl: int = 300) -> None:
        """Сохранить значение в кэше с временем жизни (TTL)."""
        expires_at = time.time() + ttl if ttl else None
        self._store[key] = (value, expires_at)

    def delete(self, key: str) -> bool:
        """Удалить значение из кэша."""
        return self._store.pop(key, None) is not None

    def clear(self) -> None:
        """Очистить весь кэш."""
        self._store.clear()


def cache_result(ttl: int = 60):
    """Декоратор для кэширования результата функции."""
    _cache = InMemoryCache()

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            key = f"{func.__name__}:{args}:{kwargs}"
            cached = _cache.get(key)
            if cached is not None:
                return cached
            result = func(*args, **kwargs)
            _cache.set(key, result, ttl)
            return result
        return wrapper
    return decorator

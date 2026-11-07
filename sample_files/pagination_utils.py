"""Утилиты для пагинации результатов запросов."""
from dataclasses import dataclass
from typing import List, TypeVar, Generic

T = TypeVar("T")


@dataclass
class Page(Generic[T]):
    """Страница результатов с метаданными пагинации."""
    items: List[T]
    total: int
    limit: int
    offset: int

    @property
    def has_next(self) -> bool:
        """Проверить, есть ли следующая страница."""
        return self.offset + self.limit < self.total

    @property
    def has_prev(self) -> bool:
        """Проверить, есть ли предыдущая страница."""
        return self.offset > 0

    @property
    def page_number(self) -> int:
        """Получить текущий номер страницы (начиная с 1)."""
        return self.offset // self.limit + 1


def paginate(items: list, limit: int = 20, offset: int = 0) -> Page:
    """Разбить список на страницы и вернуть нужную страницу."""
    total = len(items)
    sliced = items[offset:offset + limit]
    return Page(items=sliced, total=total, limit=limit, offset=offset)


def parse_pagination_params(limit: int = 20, offset: int = 0) -> tuple:
    """Валидировать и нормализовать параметры пагинации."""
    limit = max(1, min(limit, 100))
    offset = max(0, offset)
    return limit, offset

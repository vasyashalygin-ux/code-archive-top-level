"""Утилиты для трансформации и нормализации данных."""
from typing import List, Dict, Any, Callable, Optional
import re


def flatten_dict(d: Dict, separator: str = ".", prefix: str = "") -> Dict[str, Any]:
    """Сгладить вложенный словарь в плоскую структуру с разделителем."""
    result = {}
    for key, value in d.items():
        new_key = f"{prefix}{separator}{key}" if prefix else key
        if isinstance(value, dict):
            result.update(flatten_dict(value, separator, new_key))
        else:
            result[new_key] = value
    return result


def group_by(items: List[Dict], key: str) -> Dict[str, List[Dict]]:
    """Сгруппировать список словарей по значению заданного ключа."""
    result: Dict[str, List] = {}
    for item in items:
        group_key = str(item.get(key, "unknown"))
        result.setdefault(group_key, []).append(item)
    return result


def filter_fields(data: Dict, include: List[str] = None, exclude: List[str] = None) -> Dict:
    """Отфильтровать поля словаря по спискам включения или исключения."""
    if include:
        return {k: v for k, v in data.items() if k in include}
    if exclude:
        return {k: v for k, v in data.items() if k not in exclude}
    return data


def transform_list(items: List[Any], transformer: Callable) -> List[Any]:
    """Применить функцию трансформации к каждому элементу списка."""
    return [transformer(item) for item in items]


def normalize_phone(phone: str) -> str:
    """Нормализовать номер телефона к стандартному формату +7XXXXXXXXXX."""
    digits = re.sub(r"\D", "", phone)
    if len(digits) == 11 and digits.startswith("8"):
        digits = "7" + digits[1:]
    return f"+{digits}" if len(digits) >= 10 else phone

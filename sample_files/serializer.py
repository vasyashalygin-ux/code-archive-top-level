"""Утилиты сериализации и десериализации данных."""
import json
from typing import Any, Type, TypeVar, get_type_hints
from dataclasses import asdict, fields, is_dataclass
from datetime import datetime, date

T = TypeVar("T")


class JSONSerializer:
    """Расширенный JSON-сериализатор с поддержкой специальных типов."""

    @staticmethod
    def serialize(obj: Any) -> str:
        """Сериализовать объект в JSON-строку."""
        return json.dumps(obj, default=JSONSerializer._default_handler, ensure_ascii=False)

    @staticmethod
    def deserialize(data: str, cls: Type[T] = None) -> Any:
        """Десериализовать JSON-строку в объект или словарь."""
        parsed = json.loads(data)
        if cls and is_dataclass(cls):
            return cls(**parsed)
        return parsed

    @staticmethod
    def _default_handler(obj: Any) -> Any:
        """Обработать нестандартные типы при сериализации."""
        if isinstance(obj, (datetime, date)):
            return obj.isoformat()
        if is_dataclass(obj):
            return asdict(obj)
        raise TypeError(f"Тип {type(obj)} не поддерживается сериализатором")


def to_camel_case(snake_str: str) -> str:
    """Конвертировать snake_case в camelCase."""
    parts = snake_str.split("_")
    return parts[0] + "".join(p.capitalize() for p in parts[1:])


def to_snake_case(camel_str: str) -> str:
    """Конвертировать camelCase в snake_case."""
    import re
    return re.sub(r"(?<!^)(?=[A-Z])", "_", camel_str).lower()

"""Утилиты валидации входных данных."""
import re
from typing import Any, List, Optional


def validate_email(email: str) -> bool:
    """Проверить корректность формата email-адреса."""
    pattern = r"^[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}$"
    return bool(re.match(pattern, email))


def validate_phone(phone: str) -> bool:
    """Проверить корректность формата номера телефона."""
    cleaned = re.sub(r"[\s\-\(\)\+]", "", phone)
    return cleaned.isdigit() and 7 <= len(cleaned) <= 15


def validate_password_strength(password: str) -> List[str]:
    """Проверить надёжность пароля, вернуть список ошибок."""
    errors = []
    if len(password) < 8:
        errors.append("Пароль должен содержать не менее 8 символов")
    if not re.search(r"[A-Z]", password):
        errors.append("Пароль должен содержать хотя бы одну заглавную букву")
    if not re.search(r"\d", password):
        errors.append("Пароль должен содержать хотя бы одну цифру")
    return errors


def sanitize_string(value: str, max_length: Optional[int] = None) -> str:
    """Очистить строку от опасных символов и обрезать до максимальной длины."""
    cleaned = re.sub(r'[<>"\']', "", value).strip()
    if max_length:
        cleaned = cleaned[:max_length]
    return cleaned


def require_fields(data: dict, fields: List[str]) -> List[str]:
    """Проверить наличие обязательных полей в словаре, вернуть отсутствующие."""
    return [f for f in fields if f not in data or data[f] is None]

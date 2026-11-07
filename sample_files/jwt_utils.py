"""Утилиты для работы с JSON Web Tokens."""
import base64
import hmac
import hashlib
import json
import time
from typing import Optional, Dict, Any


def encode_jwt(payload: Dict[str, Any], secret: str, expires_in: int = 3600) -> str:
    """Закодировать данные в JWT-токен с указанным временем жизни."""
    payload = {**payload, "exp": int(time.time()) + expires_in}
    header = base64.urlsafe_b64encode(json.dumps({"alg": "HS256", "typ": "JWT"}).encode()).decode().rstrip("=")
    body = base64.urlsafe_b64encode(json.dumps(payload).encode()).decode().rstrip("=")
    signature_input = f"{header}.{body}".encode()
    signature = hmac.new(secret.encode(), signature_input, hashlib.sha256).hexdigest()
    return f"{header}.{body}.{signature}"


def decode_jwt(token: str, secret: str) -> Optional[Dict[str, Any]]:
    """Декодировать и проверить JWT-токен, вернуть payload или None."""
    try:
        header, body, signature = token.split(".")
        signature_input = f"{header}.{body}".encode()
        expected_sig = hmac.new(secret.encode(), signature_input, hashlib.sha256).hexdigest()
        if not hmac.compare_digest(signature, expected_sig):
            return None
        payload = json.loads(base64.urlsafe_b64decode(body + "==").decode())
        if payload.get("exp", 0) < time.time():
            return None
        return payload
    except Exception:
        return None


def extract_user_id(token: str, secret: str) -> Optional[int]:
    """Извлечь идентификатор пользователя из JWT-токена."""
    payload = decode_jwt(token, secret)
    return payload.get("user_id") if payload else None

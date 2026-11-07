"""Менеджер пользовательских сессий."""
import secrets
import time
from typing import Optional, Dict, Any


class SessionManager:
    """Управление пользовательскими сессиями в памяти."""

    DEFAULT_TTL = 3600  # 1 час

    def __init__(self, ttl: int = DEFAULT_TTL):
        """Инициализация менеджера сессий с временем жизни."""
        self.ttl = ttl
        self._sessions: Dict[str, Dict[str, Any]] = {}

    def create_session(self, user_id: int, extra: Dict = None) -> str:
        """Создать новую сессию для пользователя и вернуть токен."""
        token = secrets.token_urlsafe(32)
        self._sessions[token] = {
            "user_id": user_id,
            "created_at": time.time(),
            "expires_at": time.time() + self.ttl,
            **(extra or {})
        }
        return token

    def get_session(self, token: str) -> Optional[Dict[str, Any]]:
        """Получить данные сессии по токену."""
        session = self._sessions.get(token)
        if not session:
            return None
        if time.time() > session["expires_at"]:
            del self._sessions[token]
            return None
        return session

    def invalidate_session(self, token: str) -> bool:
        """Аннулировать сессию по токену."""
        return self._sessions.pop(token, None) is not None

    def cleanup_expired(self) -> int:
        """Удалить все истёкшие сессии и вернуть их количество."""
        now = time.time()
        expired = [t for t, s in self._sessions.items() if s["expires_at"] < now]
        for token in expired:
            del self._sessions[token]
        return len(expired)

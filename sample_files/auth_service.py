"""Сервис аутентификации и авторизации."""
import hashlib
import secrets


class AuthService:
    """Сервис для работы с аутентификацией пользователей."""

    def __init__(self, user_repository, token_store):
        """Инициализация сервиса аутентификации."""
        self.user_repo = user_repository
        self.token_store = token_store

    def login(self, username: str, password: str) -> str:
        """Аутентификация пользователя, возвращает токен сессии."""
        user = self.user_repo.find_by_username(username)
        if not user or not self._verify_password(password, user["password_hash"]):
            raise ValueError("Неверный логин или пароль")
        token = secrets.token_hex(32)
        self.token_store.set(token, user["id"])
        return token

    def logout(self, token: str) -> bool:
        """Завершить сессию по токену."""
        return self.token_store.delete(token)

    def _verify_password(self, password: str, password_hash: str) -> bool:
        """Проверить соответствие пароля его хэшу."""
        return hashlib.sha256(password.encode()).hexdigest() == password_hash


def hash_password(password: str) -> str:
    """Хэшировать пароль для безопасного хранения."""
    return hashlib.sha256(password.encode()).hexdigest()

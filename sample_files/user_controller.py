"""Контроллер для управления пользователями."""


class UserController:
    """Контроллер HTTP-запросов для работы с пользователями."""

    def __init__(self, user_service):
        """Инициализация с сервисом пользователей."""
        self.user_service = user_service

    def get_user(self, user_id: int):
        """Получить пользователя по идентификатору."""
        return self.user_service.find_by_id(user_id)

    def create_user(self, data: dict):
        """Создать нового пользователя из переданных данных."""
        return self.user_service.create(data)

    def update_user(self, user_id: int, data: dict):
        """Обновить данные существующего пользователя."""
        return self.user_service.update(user_id, data)

    def delete_user(self, user_id: int):
        """Удалить пользователя по идентификатору."""
        return self.user_service.delete(user_id)

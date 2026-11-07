"""Сервис push-уведомлений и оповещений."""
from enum import Enum
from typing import List, Optional


class NotificationType(Enum):
    """Типы уведомлений."""
    EMAIL = "email"
    SMS = "sms"
    PUSH = "push"
    IN_APP = "in_app"


class NotificationService:
    """Сервис для отправки уведомлений пользователям по различным каналам."""

    def __init__(self, email_service=None, sms_client=None, push_client=None):
        """Инициализация сервиса с доступными каналами уведомлений."""
        self.email_service = email_service
        self.sms_client = sms_client
        self.push_client = push_client

    def notify_new_order(self, order_id: int, user_id: int) -> bool:
        """Отправить уведомление о новом заказе пользователю."""
        message = f"Ваш заказ #{order_id} успешно оформлен."
        return self._dispatch(user_id, message, NotificationType.IN_APP)

    def notify_order_shipped(self, order_id: int, tracking_number: str, user_id: int) -> bool:
        """Уведомить пользователя об отправке заказа."""
        message = f"Заказ #{order_id} отправлен. Трек-номер: {tracking_number}"
        return self._dispatch(user_id, message, NotificationType.EMAIL)

    def notify_payment_failed(self, order_id: int, user_id: int) -> bool:
        """Уведомить пользователя об ошибке оплаты."""
        message = f"Ошибка оплаты заказа #{order_id}. Проверьте данные карты."
        return self._dispatch(user_id, message, NotificationType.SMS)

    def _dispatch(self, user_id: int, message: str, channel: NotificationType) -> bool:
        """Внутренний метод маршрутизации уведомлений по каналам."""
        print(f"[{channel.value}] -> user={user_id}: {message}")
        return True

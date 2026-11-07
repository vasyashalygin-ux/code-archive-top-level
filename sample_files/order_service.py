"""Сервис управления заказами."""
from typing import List, Optional
from datetime import datetime


class OrderService:
    """Бизнес-логика обработки заказов."""

    def __init__(self, order_repo, product_repo, notification_service):
        """Инициализация сервиса заказов."""
        self.order_repo = order_repo
        self.product_repo = product_repo
        self.notifications = notification_service

    def create_order(self, user_id: int, items: List[dict]) -> dict:
        """Создать новый заказ для пользователя."""
        total = self._calculate_total(items)
        order = {
            "user_id": user_id,
            "items": items,
            "total": total,
            "status": "pending",
            "created_at": datetime.utcnow().isoformat()
        }
        order_id = self.order_repo.save(order)
        self.notifications.notify_new_order(order_id, user_id)
        return {**order, "id": order_id}

    def cancel_order(self, order_id: int, user_id: int) -> bool:
        """Отменить заказ пользователя."""
        order = self.order_repo.find_by_id(order_id)
        if not order or order["user_id"] != user_id:
            return False
        return self.order_repo.update_status(order_id, "cancelled")

    def _calculate_total(self, items: List[dict]) -> float:
        """Вычислить итоговую стоимость заказа."""
        return sum(item["price"] * item["quantity"] for item in items)

    def get_user_orders(self, user_id: int) -> List[dict]:
        """Получить все заказы пользователя."""
        return self.order_repo.find_by_user(user_id)

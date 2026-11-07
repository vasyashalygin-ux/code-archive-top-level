"""Сервис управления складскими запасами."""
from typing import Dict, List, Optional
from dataclasses import dataclass


@dataclass
class StockItem:
    """Позиция складского учёта."""
    product_id: int
    quantity: int
    reserved: int = 0

    @property
    def available(self) -> int:
        """Получить доступное к продаже количество товара."""
        return self.quantity - self.reserved


class InventoryService:
    """Сервис управления остатками товаров на складе."""

    def __init__(self, inventory_repo):
        """Инициализация сервиса инвентаризации."""
        self.repo = inventory_repo

    def check_availability(self, product_id: int, quantity: int) -> bool:
        """Проверить доступность товара в указанном количестве."""
        item = self.repo.get(product_id)
        if not item:
            return False
        return item.available >= quantity

    def reserve_stock(self, product_id: int, quantity: int) -> bool:
        """Зарезервировать товар под заказ."""
        item = self.repo.get(product_id)
        if not item or item.available < quantity:
            return False
        item.reserved += quantity
        self.repo.save(item)
        return True

    def release_stock(self, product_id: int, quantity: int) -> bool:
        """Освободить ранее зарезервированный товар."""
        item = self.repo.get(product_id)
        if not item:
            return False
        item.reserved = max(0, item.reserved - quantity)
        self.repo.save(item)
        return True

    def deduct_stock(self, product_id: int, quantity: int) -> bool:
        """Списать товар со склада после подтверждения заказа."""
        item = self.repo.get(product_id)
        if not item or item.quantity < quantity:
            return False
        item.quantity -= quantity
        item.reserved = max(0, item.reserved - quantity)
        self.repo.save(item)
        return True

    def get_low_stock_alerts(self, threshold: int = 10) -> List[dict]:
        """Получить список товаров с недостаточным остатком."""
        all_items = self.repo.get_all()
        return [
            {"product_id": i.product_id, "available": i.available}
            for i in all_items if i.available <= threshold
        ]

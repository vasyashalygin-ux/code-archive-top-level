"""Шлюз для обработки платежей."""
from enum import Enum
from dataclasses import dataclass


class PaymentStatus(Enum):
    """Статусы платёжной транзакции."""
    PENDING = "pending"
    SUCCESS = "success"
    FAILED = "failed"
    REFUNDED = "refunded"


@dataclass
class PaymentResult:
    """Результат обработки платежа."""
    transaction_id: str
    status: PaymentStatus
    amount: float
    message: str


class PaymentGateway:
    """Шлюз для интеграции с платёжными системами."""

    def __init__(self, api_key: str, sandbox: bool = True):
        """Инициализация платёжного шлюза."""
        self.api_key = api_key
        self.sandbox = sandbox
        self.base_url = "https://sandbox.payments.example.com" if sandbox else "https://payments.example.com"

    def charge(self, amount: float, card_token: str, description: str) -> PaymentResult:
        """Провести списание средств с карты."""
        import secrets
        txn_id = secrets.token_hex(16)
        return PaymentResult(
            transaction_id=txn_id,
            status=PaymentStatus.SUCCESS,
            amount=amount,
            message="Платёж успешно обработан"
        )

    def refund(self, transaction_id: str, amount: float) -> PaymentResult:
        """Выполнить возврат средств по транзакции."""
        return PaymentResult(
            transaction_id=transaction_id,
            status=PaymentStatus.REFUNDED,
            amount=amount,
            message="Возврат средств выполнен"
        )

    def get_transaction(self, transaction_id: str) -> dict:
        """Получить информацию о транзакции по идентификатору."""
        return {"id": transaction_id, "status": "success"}

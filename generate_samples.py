"""Script to generate 30 sample Python files for the dataset."""
import os

samples = {
    "user_controller.py": '''"""Контроллер для управления пользователями."""


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
''',

    "auth_service.py": '''"""Сервис аутентификации и авторизации."""
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
''',

    "product_repository.py": '''"""Репозиторий для работы с продуктами в базе данных."""
import sqlite3
from typing import Optional, List


class ProductRepository:
    """Репозиторий товаров с поддержкой CRUD-операций."""

    def __init__(self, db_path: str):
        """Инициализация репозитория с путём к базе данных."""
        self.db_path = db_path

    def find_by_id(self, product_id: int) -> Optional[dict]:
        """Найти товар по идентификатору."""
        with sqlite3.connect(self.db_path) as conn:
            row = conn.execute(
                "SELECT * FROM products WHERE id = ?", (product_id,)
            ).fetchone()
            return dict(row) if row else None

    def find_all(self, limit: int = 100, offset: int = 0) -> List[dict]:
        """Получить список всех товаров с пагинацией."""
        with sqlite3.connect(self.db_path) as conn:
            rows = conn.execute(
                "SELECT * FROM products LIMIT ? OFFSET ?", (limit, offset)
            ).fetchall()
            return [dict(r) for r in rows]

    def save(self, product: dict) -> int:
        """Сохранить новый товар и вернуть его идентификатор."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                "INSERT INTO products (name, price, stock) VALUES (?, ?, ?)",
                (product["name"], product["price"], product["stock"])
            )
            return cursor.lastrowid

    def delete(self, product_id: int) -> bool:
        """Удалить товар по идентификатору."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("DELETE FROM products WHERE id = ?", (product_id,))
            return True
''',

    "email_service.py": '''"""Сервис отправки электронной почты."""
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


class EmailService:
    """Сервис для отправки email-уведомлений."""

    def __init__(self, smtp_host: str, smtp_port: int, username: str, password: str):
        """Инициализация SMTP-соединения."""
        self.smtp_host = smtp_host
        self.smtp_port = smtp_port
        self.username = username
        self.password = password

    def send_welcome(self, to_email: str, username: str) -> bool:
        """Отправить приветственное письмо новому пользователю."""
        subject = f"Добро пожаловать, {username}!"
        body = f"Ваш аккаунт успешно создан."
        return self._send(to_email, subject, body)

    def send_reset_password(self, to_email: str, reset_link: str) -> bool:
        """Отправить письмо со ссылкой для сброса пароля."""
        subject = "Сброс пароля"
        body = f"Перейдите по ссылке для сброса пароля: {reset_link}"
        return self._send(to_email, subject, body)

    def _send(self, to_email: str, subject: str, body: str) -> bool:
        """Внутренний метод отправки письма через SMTP."""
        msg = MIMEMultipart()
        msg["From"] = self.username
        msg["To"] = to_email
        msg["Subject"] = subject
        msg.attach(MIMEText(body, "plain"))
        with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
            server.login(self.username, self.password)
            server.send_message(msg)
        return True
''',

    "order_service.py": '''"""Сервис управления заказами."""
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
''',

    "cache_utils.py": '''"""Утилиты для кэширования данных."""
import time
from typing import Any, Optional
from functools import wraps


class InMemoryCache:
    """Простой кэш в памяти с поддержкой TTL."""

    def __init__(self):
        """Инициализация пустого кэша."""
        self._store = {}

    def get(self, key: str) -> Optional[Any]:
        """Получить значение из кэша по ключу."""
        entry = self._store.get(key)
        if not entry:
            return None
        value, expires_at = entry
        if expires_at and time.time() > expires_at:
            del self._store[key]
            return None
        return value

    def set(self, key: str, value: Any, ttl: int = 300) -> None:
        """Сохранить значение в кэше с временем жизни (TTL)."""
        expires_at = time.time() + ttl if ttl else None
        self._store[key] = (value, expires_at)

    def delete(self, key: str) -> bool:
        """Удалить значение из кэша."""
        return self._store.pop(key, None) is not None

    def clear(self) -> None:
        """Очистить весь кэш."""
        self._store.clear()


def cache_result(ttl: int = 60):
    """Декоратор для кэширования результата функции."""
    _cache = InMemoryCache()

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            key = f"{func.__name__}:{args}:{kwargs}"
            cached = _cache.get(key)
            if cached is not None:
                return cached
            result = func(*args, **kwargs)
            _cache.set(key, result, ttl)
            return result
        return wrapper
    return decorator
''',

    "payment_gateway.py": '''"""Шлюз для обработки платежей."""
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
''',

    "file_storage.py": '''"""Сервис для работы с файловым хранилищем."""
import os
import shutil
from pathlib import Path
from typing import Optional


class FileStorage:
    """Локальное файловое хранилище для загрузки и хранения файлов."""

    ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif", ".pdf", ".docx"}

    def __init__(self, base_dir: str):
        """Инициализация хранилища с базовой директорией."""
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(parents=True, exist_ok=True)

    def save_file(self, source_path: str, filename: str) -> str:
        """Сохранить файл в хранилище и вернуть его относительный путь."""
        ext = Path(filename).suffix.lower()
        if ext not in self.ALLOWED_EXTENSIONS:
            raise ValueError(f"Недопустимое расширение файла: {ext}")
        dest = self.base_dir / filename
        shutil.copy2(source_path, dest)
        return str(dest)

    def delete_file(self, filename: str) -> bool:
        """Удалить файл из хранилища."""
        target = self.base_dir / filename
        if target.exists():
            target.unlink()
            return True
        return False

    def get_file_path(self, filename: str) -> Optional[str]:
        """Получить полный путь к файлу в хранилище."""
        target = self.base_dir / filename
        return str(target) if target.exists() else None

    def list_files(self, extension: Optional[str] = None):
        """Получить список всех файлов в хранилище."""
        files = list(self.base_dir.iterdir())
        if extension:
            files = [f for f in files if f.suffix == extension]
        return [f.name for f in files]
''',

    "notification_service.py": '''"""Сервис push-уведомлений и оповещений."""
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
''',

    "pagination_utils.py": '''"""Утилиты для пагинации результатов запросов."""
from dataclasses import dataclass
from typing import List, TypeVar, Generic

T = TypeVar("T")


@dataclass
class Page(Generic[T]):
    """Страница результатов с метаданными пагинации."""
    items: List[T]
    total: int
    limit: int
    offset: int

    @property
    def has_next(self) -> bool:
        """Проверить, есть ли следующая страница."""
        return self.offset + self.limit < self.total

    @property
    def has_prev(self) -> bool:
        """Проверить, есть ли предыдущая страница."""
        return self.offset > 0

    @property
    def page_number(self) -> int:
        """Получить текущий номер страницы (начиная с 1)."""
        return self.offset // self.limit + 1


def paginate(items: list, limit: int = 20, offset: int = 0) -> Page:
    """Разбить список на страницы и вернуть нужную страницу."""
    total = len(items)
    sliced = items[offset:offset + limit]
    return Page(items=sliced, total=total, limit=limit, offset=offset)


def parse_pagination_params(limit: int = 20, offset: int = 0) -> tuple:
    """Валидировать и нормализовать параметры пагинации."""
    limit = max(1, min(limit, 100))
    offset = max(0, offset)
    return limit, offset
''',

    "logging_middleware.py": '''"""Middleware для логирования HTTP-запросов."""
import time
import logging
from typing import Callable

logger = logging.getLogger(__name__)


class RequestLoggingMiddleware:
    """Middleware для записи логов входящих HTTP-запросов и ответов."""

    def __init__(self, app, log_body: bool = False):
        """Инициализация middleware с настройками логирования."""
        self.app = app
        self.log_body = log_body

    async def __call__(self, scope, receive, send):
        """Обработать запрос и записать лог с временем выполнения."""
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
        start = time.time()
        method = scope.get("method", "")
        path = scope.get("path", "")
        await self.app(scope, receive, send)
        duration = (time.time() - start) * 1000
        logger.info(f"{method} {path} completed in {duration:.2f}ms")


def setup_logging(level: str = "INFO") -> None:
    """Настроить базовое логирование для приложения."""
    logging.basicConfig(
        level=getattr(logging, level.upper()),
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
    )
''',

    "config_loader.py": '''"""Загрузчик конфигурации приложения из файлов и переменных среды."""
import os
import json
from pathlib import Path
from typing import Any, Optional


class ConfigLoader:
    """Загрузчик конфигурации с поддержкой нескольких источников."""

    def __init__(self, config_path: Optional[str] = None):
        """Инициализация с опциональным путём к файлу конфигурации."""
        self._config = {}
        if config_path:
            self.load_from_file(config_path)
        self.load_from_env()

    def load_from_file(self, path: str) -> None:
        """Загрузить конфигурацию из JSON-файла."""
        with open(path) as f:
            self._config.update(json.load(f))

    def load_from_env(self, prefix: str = "APP_") -> None:
        """Загрузить конфигурацию из переменных окружения с заданным префиксом."""
        for key, value in os.environ.items():
            if key.startswith(prefix):
                clean_key = key[len(prefix):].lower()
                self._config[clean_key] = value

    def get(self, key: str, default: Any = None) -> Any:
        """Получить значение конфигурации по ключу."""
        return self._config.get(key, default)

    def require(self, key: str) -> Any:
        """Получить обязательное значение конфигурации (ошибка если отсутствует)."""
        if key not in self._config:
            raise KeyError(f"Обязательный параметр конфигурации отсутствует: {key}")
        return self._config[key]
''',

    "rate_limiter.py": '''"""Ограничитель частоты запросов (Rate Limiter)."""
import time
from collections import defaultdict
from typing import Dict, Tuple


class RateLimiter:
    """Реализация алгоритма скользящего окна для ограничения запросов."""

    def __init__(self, max_requests: int, window_seconds: int):
        """Инициализация лимитера с параметрами окна."""
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self._requests: Dict[str, list] = defaultdict(list)

    def is_allowed(self, client_id: str) -> bool:
        """Проверить, разрешён ли запрос для данного клиента."""
        now = time.time()
        window_start = now - self.window_seconds
        self._requests[client_id] = [
            t for t in self._requests[client_id] if t > window_start
        ]
        if len(self._requests[client_id]) >= self.max_requests:
            return False
        self._requests[client_id].append(now)
        return True

    def get_remaining(self, client_id: str) -> int:
        """Получить количество оставшихся разрешённых запросов."""
        return max(0, self.max_requests - len(self._requests.get(client_id, [])))

    def reset(self, client_id: str) -> None:
        """Сбросить счётчик запросов для клиента."""
        self._requests.pop(client_id, None)
''',

    "health_check.py": '''"""Эндпоинты и утилиты для проверки работоспособности сервиса."""
import time
import sqlite3
from typing import Dict, Any


class HealthChecker:
    """Компонент проверки состояния зависимостей сервиса."""

    def __init__(self, db_path: str):
        """Инициализация с путём к базе данных."""
        self.db_path = db_path
        self._start_time = time.time()

    def check_database(self) -> Dict[str, Any]:
        """Проверить доступность базы данных SQLite."""
        try:
            with sqlite3.connect(self.db_path, timeout=2) as conn:
                conn.execute("SELECT 1")
            return {"status": "ok", "latency_ms": 0}
        except Exception as e:
            return {"status": "error", "error": str(e)}

    def get_uptime(self) -> float:
        """Получить время работы сервиса в секундах."""
        return time.time() - self._start_time

    def full_check(self) -> Dict[str, Any]:
        """Выполнить полную проверку всех компонентов сервиса."""
        db_status = self.check_database()
        return {
            "status": "healthy" if db_status["status"] == "ok" else "degraded",
            "uptime_seconds": self.get_uptime(),
            "components": {
                "database": db_status
            }
        }
''',

    "search_engine.py": '''"""Простой поисковый движок с поддержкой полнотекстового поиска."""
import re
from typing import List, Dict, Any


class SearchEngine:
    """Базовый поисковый движок для индексации и поиска документов."""

    def __init__(self):
        """Инициализация поискового индекса."""
        self._index: Dict[str, List[int]] = {}
        self._documents: Dict[int, Dict] = {}
        self._next_id = 0

    def index_document(self, document: Dict[str, Any]) -> int:
        """Добавить документ в поисковый индекс."""
        doc_id = self._next_id
        self._next_id += 1
        self._documents[doc_id] = document
        text = " ".join(str(v) for v in document.values()).lower()
        for token in self._tokenize(text):
            self._index.setdefault(token, []).append(doc_id)
        return doc_id

    def search(self, query: str) -> List[Dict]:
        """Найти документы по поисковому запросу."""
        tokens = self._tokenize(query.lower())
        if not tokens:
            return []
        results = None
        for token in tokens:
            ids = set(self._index.get(token, []))
            results = ids if results is None else results & ids
        return [self._documents[i] for i in (results or [])]

    def _tokenize(self, text: str) -> List[str]:
        """Разбить текст на токены для индексации."""
        return re.findall(r"[a-zа-яё]+", text)
''',

    "jwt_utils.py": '''"""Утилиты для работы с JSON Web Tokens."""
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
''',

    "validation_utils.py": '''"""Утилиты валидации входных данных."""
import re
from typing import Any, List, Optional


def validate_email(email: str) -> bool:
    """Проверить корректность формата email-адреса."""
    pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
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
    cleaned = re.sub(r"[<>\"\'\\]", "", value).strip()
    if max_length:
        cleaned = cleaned[:max_length]
    return cleaned


def require_fields(data: dict, fields: List[str]) -> List[str]:
    """Проверить наличие обязательных полей в словаре, вернуть отсутствующие."""
    return [f for f in fields if f not in data or data[f] is None]
''',

    "database_pool.py": '''"""Пул соединений с базой данных."""
import sqlite3
import threading
from typing import Optional
from contextlib import contextmanager
from queue import Queue, Empty


class ConnectionPool:
    """Пул соединений SQLite для многопоточного использования."""

    def __init__(self, db_path: str, pool_size: int = 5):
        """Инициализация пула соединений с заданным размером."""
        self.db_path = db_path
        self.pool_size = pool_size
        self._pool: Queue = Queue(maxsize=pool_size)
        self._lock = threading.Lock()
        for _ in range(pool_size):
            conn = sqlite3.connect(db_path, check_same_thread=False)
            conn.row_factory = sqlite3.Row
            self._pool.put(conn)

    @contextmanager
    def get_connection(self, timeout: float = 5.0):
        """Получить соединение из пула в контексте менеджера."""
        conn = None
        try:
            conn = self._pool.get(timeout=timeout)
            yield conn
        except Empty:
            raise TimeoutError("Нет доступных соединений в пуле")
        finally:
            if conn:
                self._pool.put(conn)

    def close_all(self) -> None:
        """Закрыть все соединения в пуле."""
        while not self._pool.empty():
            conn = self._pool.get_nowait()
            conn.close()
''',

    "event_bus.py": '''"""Шина событий для асинхронного взаимодействия компонентов."""
from typing import Callable, Dict, List, Any
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class Event:
    """Базовый класс события с метаданными."""
    name: str
    payload: Dict[str, Any]
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())


class EventBus:
    """Шина событий с поддержкой подписок и публикаций."""

    def __init__(self):
        """Инициализация шины событий."""
        self._handlers: Dict[str, List[Callable]] = {}
        self._history: List[Event] = []

    def subscribe(self, event_name: str, handler: Callable) -> None:
        """Подписаться на событие с указанным обработчиком."""
        self._handlers.setdefault(event_name, []).append(handler)

    def unsubscribe(self, event_name: str, handler: Callable) -> bool:
        """Отписаться от события."""
        handlers = self._handlers.get(event_name, [])
        if handler in handlers:
            handlers.remove(handler)
            return True
        return False

    def publish(self, event_name: str, payload: Dict[str, Any]) -> int:
        """Опубликовать событие и вернуть количество вызванных обработчиков."""
        event = Event(name=event_name, payload=payload)
        self._history.append(event)
        handlers = self._handlers.get(event_name, [])
        for handler in handlers:
            handler(event)
        return len(handlers)

    def get_history(self, event_name: str = None) -> List[Event]:
        """Получить историю событий, опционально фильтруя по имени."""
        if event_name:
            return [e for e in self._history if e.name == event_name]
        return list(self._history)
''',

    "serializer.py": '''"""Утилиты сериализации и десериализации данных."""
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
''',

    "report_generator.py": '''"""Генератор отчётов в различных форматах."""
import csv
import io
import json
from typing import List, Dict, Any


class ReportGenerator:
    """Генератор отчётов с поддержкой CSV и JSON форматов."""

    def __init__(self, title: str):
        """Инициализация генератора с заголовком отчёта."""
        self.title = title
        self._rows: List[Dict[str, Any]] = []

    def add_row(self, row: Dict[str, Any]) -> None:
        """Добавить строку данных в отчёт."""
        self._rows.append(row)

    def add_rows(self, rows: List[Dict[str, Any]]) -> None:
        """Добавить несколько строк данных в отчёт."""
        self._rows.extend(rows)

    def to_csv(self) -> str:
        """Экспортировать отчёт в формат CSV."""
        if not self._rows:
            return ""
        output = io.StringIO()
        writer = csv.DictWriter(output, fieldnames=self._rows[0].keys())
        writer.writeheader()
        writer.writerows(self._rows)
        return output.getvalue()

    def to_json(self) -> str:
        """Экспортировать отчёт в формат JSON."""
        return json.dumps({
            "title": self.title,
            "count": len(self._rows),
            "data": self._rows
        }, ensure_ascii=False, indent=2)

    def summary(self) -> Dict[str, Any]:
        """Получить краткую сводку по данным отчёта."""
        return {
            "title": self.title,
            "total_rows": len(self._rows),
            "columns": list(self._rows[0].keys()) if self._rows else []
        }
''',

    "task_queue.py": '''"""Очередь задач для фоновой обработки."""
import threading
from typing import Callable, Any, Dict, Optional
from dataclasses import dataclass, field
from queue import Queue
from enum import Enum
import uuid


class TaskStatus(Enum):
    """Статусы задачи в очереди."""
    PENDING = "pending"
    RUNNING = "running"
    DONE = "done"
    FAILED = "failed"


@dataclass
class Task:
    """Задача для фоновой обработки."""
    id: str
    func: Callable
    args: tuple
    kwargs: Dict
    status: TaskStatus = TaskStatus.PENDING
    result: Any = None
    error: Optional[str] = None


class TaskQueue:
    """Простая очередь задач с пулом рабочих потоков."""

    def __init__(self, workers: int = 2):
        """Инициализация очереди с заданным числом воркеров."""
        self._queue: Queue = Queue()
        self._tasks: Dict[str, Task] = {}
        self._workers = workers
        self._running = False

    def submit(self, func: Callable, *args, **kwargs) -> str:
        """Поставить задачу в очередь и вернуть её идентификатор."""
        task_id = str(uuid.uuid4())
        task = Task(id=task_id, func=func, args=args, kwargs=kwargs)
        self._tasks[task_id] = task
        self._queue.put(task)
        return task_id

    def get_status(self, task_id: str) -> Optional[TaskStatus]:
        """Получить статус задачи по идентификатору."""
        task = self._tasks.get(task_id)
        return task.status if task else None

    def start(self) -> None:
        """Запустить рабочие потоки очереди."""
        self._running = True
        for _ in range(self._workers):
            thread = threading.Thread(target=self._worker, daemon=True)
            thread.start()

    def _worker(self) -> None:
        """Внутренний рабочий процесс обработки задач из очереди."""
        while self._running:
            try:
                task = self._queue.get(timeout=1)
                task.status = TaskStatus.RUNNING
                task.result = task.func(*task.args, **task.kwargs)
                task.status = TaskStatus.DONE
            except Exception as e:
                task.status = TaskStatus.FAILED
                task.error = str(e)
''',

    "migration_runner.py": '''"""Система миграций базы данных."""
import sqlite3
import os
from typing import List
from pathlib import Path


class MigrationRunner:
    """Исполнитель миграций схемы базы данных."""

    def __init__(self, db_path: str, migrations_dir: str):
        """Инициализация с путями к БД и директории с миграциями."""
        self.db_path = db_path
        self.migrations_dir = Path(migrations_dir)

    def _ensure_migrations_table(self, conn: sqlite3.Connection) -> None:
        """Создать таблицу для отслеживания применённых миграций."""
        conn.execute("""
            CREATE TABLE IF NOT EXISTS _migrations (
                id INTEGER PRIMARY KEY,
                name TEXT UNIQUE NOT NULL,
                applied_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)

    def get_applied_migrations(self, conn: sqlite3.Connection) -> List[str]:
        """Получить список уже применённых миграций."""
        rows = conn.execute("SELECT name FROM _migrations ORDER BY id").fetchall()
        return [row[0] for row in rows]

    def run_pending(self) -> int:
        """Применить все ожидающие миграции и вернуть их количество."""
        sql_files = sorted(self.migrations_dir.glob("*.sql"))
        count = 0
        with sqlite3.connect(self.db_path) as conn:
            self._ensure_migrations_table(conn)
            applied = set(self.get_applied_migrations(conn))
            for migration_file in sql_files:
                if migration_file.name not in applied:
                    sql = migration_file.read_text()
                    conn.executescript(sql)
                    conn.execute("INSERT INTO _migrations (name) VALUES (?)", (migration_file.name,))
                    count += 1
        return count

    def rollback_last(self) -> bool:
        """Откатить последнюю применённую миграцию."""
        with sqlite3.connect(self.db_path) as conn:
            last = conn.execute("SELECT name FROM _migrations ORDER BY id DESC LIMIT 1").fetchone()
            if not last:
                return False
            conn.execute("DELETE FROM _migrations WHERE name = ?", (last[0],))
            return True
''',

    "session_manager.py": '''"""Менеджер пользовательских сессий."""
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
''',

    "api_client.py": '''"""Базовый HTTP-клиент для взаимодействия с внешними API."""
import urllib.request
import urllib.error
import json
from typing import Optional, Dict, Any


class ApiClient:
    """Базовый клиент для HTTP-запросов к REST API."""

    def __init__(self, base_url: str, api_key: Optional[str] = None, timeout: int = 30):
        """Инициализация клиента с базовым URL и опциональным ключом API."""
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.timeout = timeout

    def get(self, path: str, params: Dict = None) -> Dict[str, Any]:
        """Выполнить GET-запрос к API."""
        url = f"{self.base_url}/{path.lstrip('/')}"
        if params:
            query = "&".join(f"{k}={v}" for k, v in params.items())
            url = f"{url}?{query}"
        return self._request("GET", url)

    def post(self, path: str, data: Dict) -> Dict[str, Any]:
        """Выполнить POST-запрос к API с JSON-телом."""
        url = f"{self.base_url}/{path.lstrip('/')}"
        return self._request("POST", url, data)

    def _request(self, method: str, url: str, data: Dict = None) -> Dict[str, Any]:
        """Внутренний метод для выполнения HTTP-запроса."""
        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        body = json.dumps(data).encode() if data else None
        req = urllib.request.Request(url, data=body, headers=headers, method=method)
        try:
            with urllib.request.urlopen(req, timeout=self.timeout) as resp:
                return json.loads(resp.read().decode())
        except urllib.error.HTTPError as e:
            raise RuntimeError(f"API вернул ошибку {e.code}: {e.reason}")
''',

    "audit_log.py": '''"""Аудит-лог для отслеживания действий пользователей."""
import sqlite3
import json
from datetime import datetime
from typing import List, Dict, Any, Optional


class AuditLog:
    """Система аудита для записи и хранения действий пользователей."""

    def __init__(self, db_path: str):
        """Инициализация аудит-лога с базой данных."""
        self.db_path = db_path
        self._init_table()

    def _init_table(self) -> None:
        """Создать таблицу аудита, если она не существует."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS audit_log (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    action TEXT NOT NULL,
                    resource TEXT,
                    details TEXT,
                    ip_address TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            """)

    def log_action(self, user_id: int, action: str, resource: str = None,
                   details: Dict = None, ip_address: str = None) -> int:
        """Записать действие пользователя в аудит-лог."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                "INSERT INTO audit_log (user_id, action, resource, details, ip_address) VALUES (?, ?, ?, ?, ?)",
                (user_id, action, resource, json.dumps(details) if details else None, ip_address)
            )
            return cursor.lastrowid

    def get_user_actions(self, user_id: int, limit: int = 50) -> List[Dict[str, Any]]:
        """Получить историю действий пользователя."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            rows = conn.execute(
                "SELECT * FROM audit_log WHERE user_id = ? ORDER BY created_at DESC LIMIT ?",
                (user_id, limit)
            ).fetchall()
            return [dict(r) for r in rows]

    def get_actions_by_type(self, action: str) -> List[Dict[str, Any]]:
        """Получить все действия определённого типа из аудит-лога."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            rows = conn.execute(
                "SELECT * FROM audit_log WHERE action = ? ORDER BY created_at DESC",
                (action,)
            ).fetchall()
            return [dict(r) for r in rows]
''',

    "data_transformer.py": '''"""Утилиты для трансформации и нормализации данных."""
from typing import List, Dict, Any, Callable, Optional
import re


def flatten_dict(d: Dict, separator: str = ".", prefix: str = "") -> Dict[str, Any]:
    """Сгладить вложенный словарь в плоскую структуру с разделителем."""
    result = {}
    for key, value in d.items():
        new_key = f"{prefix}{separator}{key}" if prefix else key
        if isinstance(value, dict):
            result.update(flatten_dict(value, separator, new_key))
        else:
            result[new_key] = value
    return result


def group_by(items: List[Dict], key: str) -> Dict[str, List[Dict]]:
    """Сгруппировать список словарей по значению заданного ключа."""
    result: Dict[str, List] = {}
    for item in items:
        group_key = str(item.get(key, "unknown"))
        result.setdefault(group_key, []).append(item)
    return result


def filter_fields(data: Dict, include: List[str] = None, exclude: List[str] = None) -> Dict:
    """Отфильтровать поля словаря по спискам включения или исключения."""
    if include:
        return {k: v for k, v in data.items() if k in include}
    if exclude:
        return {k: v for k, v in data.items() if k not in exclude}
    return data


def transform_list(items: List[Any], transformer: Callable) -> List[Any]:
    """Применить функцию трансформации к каждому элементу списка."""
    return [transformer(item) for item in items]


def normalize_phone(phone: str) -> str:
    """Нормализовать номер телефона к стандартному формату +7XXXXXXXXXX."""
    digits = re.sub(r"\D", "", phone)
    if len(digits) == 11 and digits.startswith("8"):
        digits = "7" + digits[1:]
    return f"+{digits}" if len(digits) >= 10 else phone
''',

    "scheduler.py": '''"""Планировщик периодических задач."""
import threading
import time
from typing import Callable, Dict, Optional
from dataclasses import dataclass


@dataclass
class ScheduledJob:
    """Конфигурация периодической задачи."""
    name: str
    func: Callable
    interval_seconds: int
    last_run: float = 0.0
    run_count: int = 0
    enabled: bool = True


class Scheduler:
    """Простой планировщик задач на основе потоков."""

    def __init__(self):
        """Инициализация пустого планировщика."""
        self._jobs: Dict[str, ScheduledJob] = {}
        self._running = False
        self._thread: Optional[threading.Thread] = None

    def add_job(self, name: str, func: Callable, interval_seconds: int) -> None:
        """Добавить периодическую задачу в планировщик."""
        self._jobs[name] = ScheduledJob(
            name=name, func=func, interval_seconds=interval_seconds
        )

    def remove_job(self, name: str) -> bool:
        """Удалить задачу из планировщика по имени."""
        return self._jobs.pop(name, None) is not None

    def start(self) -> None:
        """Запустить планировщик в фоновом потоке."""
        self._running = True
        self._thread = threading.Thread(target=self._run_loop, daemon=True)
        self._thread.start()

    def stop(self) -> None:
        """Остановить планировщик."""
        self._running = False
        if self._thread:
            self._thread.join(timeout=5)

    def _run_loop(self) -> None:
        """Основной цикл планировщика, проверяющий и запускающий задачи."""
        while self._running:
            now = time.time()
            for job in self._jobs.values():
                if job.enabled and now - job.last_run >= job.interval_seconds:
                    try:
                        job.func()
                        job.run_count += 1
                        job.last_run = now
                    except Exception as e:
                        print(f"Ошибка в задаче {job.name}: {e}")
            time.sleep(1)
''',

    "inventory_service.py": '''"""Сервис управления складскими запасами."""
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
''',

    "user_repository.py": '''"""Репозиторий для работы с данными пользователей."""
import sqlite3
from typing import Optional, List, Dict, Any


class UserRepository:
    """Репозиторий пользователей с поддержкой базовых операций."""

    def __init__(self, db_path: str):
        """Инициализация репозитория с путём к базе данных."""
        self.db_path = db_path
        self._init_schema()

    def _init_schema(self) -> None:
        """Создать таблицу пользователей, если она не существует."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    email TEXT UNIQUE NOT NULL,
                    password_hash TEXT NOT NULL,
                    is_active INTEGER DEFAULT 1,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            """)

    def find_by_id(self, user_id: int) -> Optional[Dict]:
        """Найти пользователя по уникальному идентификатору."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            row = conn.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
            return dict(row) if row else None

    def find_by_username(self, username: str) -> Optional[Dict]:
        """Найти пользователя по имени пользователя."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            row = conn.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()
            return dict(row) if row else None

    def create(self, username: str, email: str, password_hash: str) -> int:
        """Создать нового пользователя и вернуть его идентификатор."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                "INSERT INTO users (username, email, password_hash) VALUES (?, ?, ?)",
                (username, email, password_hash)
            )
            return cursor.lastrowid

    def update_email(self, user_id: int, new_email: str) -> bool:
        """Обновить email-адрес пользователя."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("UPDATE users SET email = ? WHERE id = ?", (new_email, user_id))
            return True

    def deactivate(self, user_id: int) -> bool:
        """Деактивировать учётную запись пользователя."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("UPDATE users SET is_active = 0 WHERE id = ?", (user_id,))
            return True
''',
}

os.makedirs("sample_files", exist_ok=True)
for filename, content in samples.items():
    with open(f"sample_files/{filename}", "w", encoding="utf-8") as f:
        f.write(content)

print(f"Создано {len(samples)} файлов в sample_files/")

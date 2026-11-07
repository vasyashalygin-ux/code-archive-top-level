"""Middleware для логирования HTTP-запросов."""
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

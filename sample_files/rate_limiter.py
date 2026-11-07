"""Ограничитель частоты запросов (Rate Limiter)."""
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

"""Шина событий для асинхронного взаимодействия компонентов."""
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

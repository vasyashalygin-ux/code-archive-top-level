"""Очередь задач для фоновой обработки."""
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

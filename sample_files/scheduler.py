"""Планировщик периодических задач."""
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

"""Загрузчик конфигурации приложения из файлов и переменных среды."""
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

# Используем официальный образ Python 3.12 (slim для экономии места)
FROM python:3.12-slim

# Метаданные образа
LABEL maintainer="Топ Уровень — Ростелеком ИТ Школа"
LABEL description="Архив кода — API для навигации по кодовой базе"

# Рабочая директория внутри контейнера
WORKDIR /app

# Сначала копируем зависимости (используем Docker layer cache)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копируем исходный код
COPY indexer.py .
COPY main.py .
COPY sample_files/ ./sample_files/

# Запускаем индексатор при сборке образа
RUN python indexer.py ./sample_files code_archive.db

# Порт API
EXPOSE 8000

# Healthcheck — проверяем /api/stats каждые 30 секунд
HEALTHCHECK --interval=30s --timeout=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/api/stats')" || exit 1

# Запуск API
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]

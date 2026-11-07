# «Архив кода» — API для навигации по кодовой базе

REST-сервис на Python, который индексирует `.py`-файлы и позволяет искать функции и классы по имени или описанию.

**Чемпионат «Топ Уровень» — Ростелеком ИТ Школа**

---

## Содержание

- [Архитектура и схема БД](#схема-бд)
- [Быстрый старт](#быстрый-старт)
- [Запуск через Docker](#docker)
- [Эндпоинты API](#эндпоинты)
- [Примеры запросов](#примеры-запросов)
- [Структура проекта](#структура-проекта)

---

## Схема БД

База данных SQLite (`code_archive.db`) состоит из двух таблиц.

### Таблица `files`
Хранит информацию о проиндексированных файлах.

| Колонка      | Тип     | Описание                              |
|--------------|---------|---------------------------------------|
| `id`         | INTEGER | Первичный ключ (автоинкремент)        |
| `filename`   | TEXT    | Имя файла (уникальное), напр. `auth_service.py` |
| `filepath`   | TEXT    | Абсолютный путь к файлу              |
| `indexed_at` | TEXT    | Дата и время последней индексации    |

### Таблица `entities`
Хранит функции и классы, извлечённые из файлов.

| Колонка      | Тип     | Описание                                      |
|--------------|---------|-----------------------------------------------|
| `id`         | INTEGER | Первичный ключ (автоинкремент)                |
| `file_id`    | INTEGER | Внешний ключ → `files.id`                    |
| `name`       | TEXT    | Имя функции или класса                        |
| `kind`       | TEXT    | Тип: `function` или `class`                  |
| `line_start` | INTEGER | Номер строки начала определения               |
| `line_end`   | INTEGER | Номер строки конца определения                |
| `docstring`  | TEXT    | Docstring (первый строковый литерал), может быть NULL |
| `parent`     | TEXT    | Имя класса-родителя для методов, NULL для top-level |

### Индексы

```sql
-- Ускоряют поиск по имени и типу (основные операции поиска)
CREATE INDEX idx_entities_name      ON entities(name);
CREATE INDEX idx_entities_kind      ON entities(kind);
CREATE INDEX idx_entities_file_id   ON entities(file_id);
CREATE INDEX idx_entities_docstring ON entities(docstring);
```

**Почему SQLite, а не PostgreSQL?**
Для датасета из 30–1000 файлов SQLite полностью достаточен. Он встроен в Python (не нужна установка), файл `.db` хранится прямо в репозитории, а LIKE-поиск с индексом работает на миллионах строк без заметных задержек.

---

## Быстрый старт

### 1. Установка зависимостей

```bash
pip install -r requirements.txt
```

### 2. Индексирование датасета

```bash
# Индексировать папку sample_files (30 Python-файлов)
python indexer.py ./sample_files

# Или указать свою папку и имя БД
python indexer.py ./my_project my_archive.db
```

Вывод:
```
Найдено 30 файлов. Индексирую в «code_archive.db»...
  ✓ api_client.py                          → 3 сущностей
  ✓ audit_log.py                           → 5 сущностей
  ...
Готово! Проиндексировано файлов: 30, сущностей: 147
```

### 3. Запуск API

```bash
uvicorn main:app --reload
```

API доступен на `http://localhost:8000`  
Swagger UI: `http://localhost:8000/docs`

---

## Docker

### Сборка и запуск одной командой

```bash
# Собрать образ
docker build -t code-archive .

# Запустить контейнер
docker run -p 8000:8000 code-archive
```

### Монтирование своей папки с кодом

```bash
docker run -p 8000:8000 \
  -v /path/to/my/code:/app/custom_code \
  -e DB_PATH=/app/custom.db \
  code-archive
```

---

## Эндпоинты

| Метод | URL | Описание |
|-------|-----|----------|
| GET | `/api/files` | Список всех проиндексированных файлов (с пагинацией) |
| GET | `/api/files/{name}/structure` | Структура конкретного файла |
| GET | `/api/search?q={keyword}` | Поиск по имени или docstring |
| GET | `/api/stats` | Сводная статистика (бонус) |

### Параметры запросов

**`GET /api/files`**
- `limit` (int, 1–100, по умолчанию 20) — записей на страницу
- `offset` (int, ≥0, по умолчанию 0) — смещение

**`GET /api/search`**
- `q` (string, обязательный) — ключевое слово
- `type` (string, опциональный) — `function` или `class`
- `limit`, `offset` — пагинация

---

## Примеры запросов

### 1. Получить список всех файлов

```bash
curl http://localhost:8000/api/files
```

```json
{
  "items": [
    {
      "id": 1,
      "filename": "api_client.py",
      "filepath": "/app/sample_files/api_client.py",
      "indexed_at": "2026-05-18 10:00:00",
      "entity_count": 3
    },
    {
      "id": 2,
      "filename": "auth_service.py",
      "filepath": "/app/sample_files/auth_service.py",
      "indexed_at": "2026-05-18 10:00:00",
      "entity_count": 4
    }
  ],
  "total": 30,
  "limit": 20,
  "offset": 0,
  "has_next": true,
  "has_prev": false
}
```

### 2. Получить структуру файла

```bash
curl http://localhost:8000/api/files/auth_service.py/structure
```

```json
{
  "id": 2,
  "filename": "auth_service.py",
  "filepath": "/app/sample_files/auth_service.py",
  "indexed_at": "2026-05-18 10:00:00",
  "entities": [
    {
      "id": 5,
      "name": "AuthService",
      "kind": "class",
      "line_start": 7,
      "line_end": 38,
      "docstring": "Сервис для работы с аутентификацией пользователей.",
      "parent": null,
      "filename": "auth_service.py"
    },
    {
      "id": 6,
      "name": "login",
      "kind": "function",
      "line_start": 12,
      "line_end": 21,
      "docstring": "Аутентификация пользователя, возвращает токен сессии.",
      "parent": "AuthService",
      "filename": "auth_service.py"
    }
  ]
}
```

### 3. Поиск по ключевому слову

```bash
curl "http://localhost:8000/api/search?q=пользователь"
```

```json
{
  "items": [
    {
      "id": 6,
      "name": "login",
      "kind": "function",
      "line_start": 12,
      "line_end": 21,
      "docstring": "Аутентификация пользователя, возвращает токен сессии.",
      "parent": "AuthService",
      "filename": "auth_service.py"
    }
  ],
  "total": 1,
  "limit": 20,
  "offset": 0,
  "has_next": false,
  "has_prev": false
}
```

### 4. Поиск только классов

```bash
curl "http://localhost:8000/api/search?q=сервис&type=class"
```

```json
{
  "items": [
    {
      "id": 5,
      "name": "AuthService",
      "kind": "class",
      ...
    },
    {
      "id": 40,
      "name": "EmailService",
      "kind": "class",
      ...
    }
  ],
  "total": 8,
  "limit": 20,
  "offset": 0,
  "has_next": false,
  "has_prev": false
}
```

### 5. Сводная статистика

```bash
curl http://localhost:8000/api/stats
```

```json
{
  "total_files": 30,
  "total_entities": 147,
  "total_functions": 112,
  "total_classes": 35
}
```

---

## Структура проекта

```
code_archive/
├── indexer.py          # Часть A: индексатор (парсинг AST → SQLite)
├── main.py             # Часть B: FastAPI REST API
├── requirements.txt    # Зависимости
├── Dockerfile          # Бонус: Docker-сборка
├── README.md           # Документация
├── code_archive.db     # SQLite-база (создаётся индексатором)
└── sample_files/       # 30 тестовых Python-файлов
    ├── auth_service.py
    ├── cache_utils.py
    └── ...
```

---

## Технический стек

| Компонент | Технология | Примечание |
|-----------|-----------|------------|
| Язык | Python 3.12 | Единственный язык проекта |
| Парсинг кода | `ast` (встроенный) | Никаких сторонних парсеров |
| База данных | SQLite (`sqlite3`) | Файл `.db` в репозитории |
| REST API | FastAPI + uvicorn | Swagger из коробки на `/docs` |
| Валидация | Pydantic v2 | Автоматические JSON-схемы |
| Контейнеризация | Docker | Бонусный элемент |

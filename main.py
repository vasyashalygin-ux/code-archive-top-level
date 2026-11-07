"""
«Архив кода» — REST API для навигации по кодовой базе.

Часть B: FastAPI-приложение с тремя основными и двумя бонусными эндпоинтами.

Запуск:
    uvicorn main:app --reload

Документация Swagger: http://localhost:8000/docs
"""
import sqlite3
from contextlib import contextmanager
from typing import List, Optional

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# ─── Путь к базе данных (можно переопределить через переменную окружения) ─────
import os
DB_PATH = os.getenv("DB_PATH", "code_archive.db")


# ─────────────────────────── Pydantic-схемы ──────────────────────────────────

class EntityInfo(BaseModel):
    """Краткая информация о функции или классе."""
    id: int
    name: str
    kind: str                     # "function" | "class"
    line_start: int
    line_end: int
    docstring: Optional[str]
    parent: Optional[str]         # имя класса-родителя (для методов)
    filename: str


class FileListItem(BaseModel):
    """Элемент списка проиндексированных файлов."""
    id: int
    filename: str
    filepath: str
    indexed_at: str
    entity_count: int             # сколько функций+классов в файле


class FileStructure(BaseModel):
    """Полная структура одного файла."""
    id: int
    filename: str
    filepath: str
    indexed_at: str
    entities: List[EntityInfo]


class StatsResponse(BaseModel):
    """Сводная статистика по всей кодовой базе."""
    total_files: int
    total_entities: int
    total_functions: int
    total_classes: int


class PaginatedFiles(BaseModel):
    """Пагинированный список файлов."""
    items: List[FileListItem]
    total: int
    limit: int
    offset: int
    has_next: bool
    has_prev: bool


class PaginatedEntities(BaseModel):
    """Пагинированный список сущностей."""
    items: List[EntityInfo]
    total: int
    limit: int
    offset: int
    has_next: bool
    has_prev: bool


# ────────────────────────── Вспомогательные функции ──────────────────────────

@contextmanager
def get_db():
    """Контекстный менеджер для получения соединения с БД."""
    if not os.path.exists(DB_PATH):
        raise HTTPException(
            status_code=503,
            detail=(
                f"База данных «{DB_PATH}» не найдена. "
                "Запустите индексатор: python indexer.py ./sample_files"
            ),
        )
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()


def row_to_entity(row: sqlite3.Row) -> EntityInfo:
    """Конвертировать строку БД в Pydantic-модель EntityInfo."""
    return EntityInfo(
        id=row["id"],
        name=row["name"],
        kind=row["kind"],
        line_start=row["line_start"],
        line_end=row["line_end"],
        docstring=row["docstring"],
        parent=row["parent"],
        filename=row["filename"],
    )


# ─────────────────────────── FastAPI-приложение ───────────────────────────────

app = FastAPI(
    title="Архив кода",
    description=(
        "REST API для навигации по проиндексированной кодовой базе Python. "
        "Позволяет искать функции и классы по имени или docstring."
    ),
    version="1.0.0",
    contact={"name": "Ростелеком ИТ Школа — Чемпионат «Топ Уровень»"},
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET"],
    allow_headers=["*"],
)


# ──────────────────────── Эндпоинты ──────────────────────────────────────────

@app.get(
    "/api/files",
    response_model=PaginatedFiles,
    summary="Список проиндексированных файлов",
    tags=["Файлы"],
)
def list_files(
    limit: int = Query(20, ge=1, le=100, description="Количество файлов на странице"),
    offset: int = Query(0, ge=0, description="Смещение (для пагинации)"),
):
    """
    Возвращает список всех проиндексированных .py-файлов
    с количеством функций и классов в каждом.

    Поддерживает пагинацию через параметры **limit** и **offset**.
    """
    with get_db() as conn:
        total = conn.execute("SELECT COUNT(*) FROM files").fetchone()[0]

        rows = conn.execute(
            """
            SELECT
                f.id,
                f.filename,
                f.filepath,
                f.indexed_at,
                COUNT(e.id) AS entity_count
            FROM files f
            LEFT JOIN entities e ON e.file_id = f.id
            GROUP BY f.id
            ORDER BY f.filename
            LIMIT ? OFFSET ?
            """,
            (limit, offset),
        ).fetchall()

        items = [
            FileListItem(
                id=r["id"],
                filename=r["filename"],
                filepath=r["filepath"],
                indexed_at=r["indexed_at"],
                entity_count=r["entity_count"],
            )
            for r in rows
        ]

    return PaginatedFiles(
        items=items,
        total=total,
        limit=limit,
        offset=offset,
        has_next=offset + limit < total,
        has_prev=offset > 0,
    )


@app.get(
    "/api/files/{name}/structure",
    response_model=FileStructure,
    summary="Структура конкретного файла",
    tags=["Файлы"],
)
def get_file_structure(name: str):
    """
    Возвращает полную структуру файла: все функции и классы
    с номерами строк и docstring.

    Параметр **name** — имя файла (например, `auth_service.py`).
    """
    with get_db() as conn:
        file_row = conn.execute(
            "SELECT * FROM files WHERE filename = ?", (name,)
        ).fetchone()

        if not file_row:
            raise HTTPException(status_code=404, detail=f"Файл «{name}» не найден в индексе")

        entity_rows = conn.execute(
            """
            SELECT e.*, f.filename
            FROM entities e
            JOIN files f ON f.id = e.file_id
            WHERE e.file_id = ?
            ORDER BY e.line_start
            """,
            (file_row["id"],),
        ).fetchall()

    return FileStructure(
        id=file_row["id"],
        filename=file_row["filename"],
        filepath=file_row["filepath"],
        indexed_at=file_row["indexed_at"],
        entities=[row_to_entity(r) for r in entity_rows],
    )


@app.get(
    "/api/search",
    response_model=PaginatedEntities,
    summary="Поиск функций и классов",
    tags=["Поиск"],
)
def search_entities(
    q: str = Query(..., min_length=1, description="Ключевое слово для поиска"),
    type: Optional[str] = Query(
        None,
        description="Фильтр по типу: `function` или `class`",
        pattern="^(function|class)$",
    ),
    limit: int = Query(20, ge=1, le=100, description="Количество результатов на странице"),
    offset: int = Query(0, ge=0, description="Смещение (для пагинации)"),
):
    """
    Полнотекстовый поиск по именам и docstring функций/классов.

    - Поиск **регистронезависимый**
    - Параметр **q** — ключевое слово (ищется в `name` и `docstring`)
    - Параметр **type** (опциональный) — фильтрует по типу сущности
    - Если ничего не найдено — возвращается `[]`, а не ошибка 500
    """
    keyword = f"%{q.lower()}%"

    type_filter = ""
    params: list = [keyword, keyword]

    if type:
        type_filter = "AND e.kind = ?"
        params.append(type)

    base_query = f"""
        FROM entities e
        JOIN files f ON f.id = e.file_id
        WHERE (LOWER(e.name) LIKE ? OR LOWER(COALESCE(e.docstring, '')) LIKE ?)
        {type_filter}
    """

    with get_db() as conn:
        total = conn.execute(f"SELECT COUNT(*) {base_query}", params).fetchone()[0]

        rows = conn.execute(
            f"""
            SELECT e.*, f.filename
            {base_query}
            ORDER BY e.name
            LIMIT ? OFFSET ?
            """,
            params + [limit, offset],
        ).fetchall()

    return PaginatedEntities(
        items=[row_to_entity(r) for r in rows],
        total=total,
        limit=limit,
        offset=offset,
        has_next=offset + limit < total,
        has_prev=offset > 0,
    )


# ──────────────────────── Бонусные эндпоинты ─────────────────────────────────

@app.get(
    "/api/stats",
    response_model=StatsResponse,
    summary="Сводная статистика по кодовой базе",
    tags=["Статистика"],
)
def get_stats():
    """
    Возвращает общую статистику:
    количество файлов, функций, классов и сущностей в индексе.
    """
    with get_db() as conn:
        total_files = conn.execute("SELECT COUNT(*) FROM files").fetchone()[0]
        total_entities = conn.execute("SELECT COUNT(*) FROM entities").fetchone()[0]
        total_functions = conn.execute(
            "SELECT COUNT(*) FROM entities WHERE kind = 'function'"
        ).fetchone()[0]
        total_classes = conn.execute(
            "SELECT COUNT(*) FROM entities WHERE kind = 'class'"
        ).fetchone()[0]

    return StatsResponse(
        total_files=total_files,
        total_entities=total_entities,
        total_functions=total_functions,
        total_classes=total_classes,
    )


@app.get("/", include_in_schema=False)
def root():
    """Редирект на документацию."""
    from fastapi.responses import RedirectResponse
    return RedirectResponse(url="/docs")

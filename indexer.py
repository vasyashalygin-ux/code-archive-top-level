"""
Индексатор кодовой базы — Часть A.

Читает .py-файлы, извлекает структуру (функции, классы, docstring)
с помощью стандартного модуля ast и сохраняет в SQLite.
"""
import ast
import sqlite3
import sys
from pathlib import Path
from typing import List, Dict, Any


# ─────────────────────────── Схема БД ────────────────────────────────────────

SCHEMA_SQL = """
-- Таблица индексированных файлов
CREATE TABLE IF NOT EXISTS files (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    filename    TEXT    NOT NULL UNIQUE,
    filepath    TEXT    NOT NULL,
    indexed_at  TEXT    DEFAULT CURRENT_TIMESTAMP
);

-- Таблица функций и классов
CREATE TABLE IF NOT EXISTS entities (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    file_id     INTEGER NOT NULL REFERENCES files(id) ON DELETE CASCADE,
    name        TEXT    NOT NULL,
    kind        TEXT    NOT NULL CHECK(kind IN ('function', 'class')),
    line_start  INTEGER NOT NULL,
    line_end    INTEGER NOT NULL,
    docstring   TEXT,
    parent      TEXT    -- имя класса-родителя для методов
);

-- Индексы для ускорения поиска
CREATE INDEX IF NOT EXISTS idx_entities_name     ON entities(name);
CREATE INDEX IF NOT EXISTS idx_entities_kind     ON entities(kind);
CREATE INDEX IF NOT EXISTS idx_entities_file_id  ON entities(file_id);
CREATE INDEX IF NOT EXISTS idx_entities_docstring ON entities(docstring);
"""


# ─────────────────────── Парсинг Python-файла ────────────────────────────────

def extract_entities(filepath: str) -> List[Dict[str, Any]]:
    """
    Извлечь все функции и классы из Python-файла через AST.

    Возвращает список словарей с полями:
      name, kind, line_start, line_end, docstring, parent
    """
    source = Path(filepath).read_text(encoding="utf-8", errors="replace")
    try:
        tree = ast.parse(source)
    except SyntaxError as exc:
        print(f"  [WARN] Синтаксическая ошибка в {filepath}: {exc}", file=sys.stderr)
        return []

    entities = []

    def _docstring(node: ast.AST) -> str | None:
        """Достать первый строковый литерал из тела как docstring."""
        if (
            isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef))
            and node.body
            and isinstance(node.body[0], ast.Expr)
            and isinstance(node.body[0].value, ast.Constant)
            and isinstance(node.body[0].value.value, str)
        ):
            return node.body[0].value.value.strip()
        return None

    def _end_line(node: ast.AST) -> int:
        """Получить последнюю строку узла AST (поддержка Python 3.8+)."""
        return getattr(node, "end_lineno", node.lineno)

    def _visit(node: ast.AST, parent_class: str | None = None) -> None:
        """Рекурсивный обход AST-дерева."""
        if isinstance(node, ast.ClassDef):
            entities.append({
                "name":       node.name,
                "kind":       "class",
                "line_start": node.lineno,
                "line_end":   _end_line(node),
                "docstring":  _docstring(node),
                "parent":     parent_class,
            })
            # Обойти методы внутри класса
            for child in ast.iter_child_nodes(node):
                _visit(child, parent_class=node.name)

        elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            entities.append({
                "name":       node.name,
                "kind":       "function",
                "line_start": node.lineno,
                "line_end":   _end_line(node),
                "docstring":  _docstring(node),
                "parent":     parent_class,
            })
            # Не углубляемся во вложенные функции (только верхний уровень внутри класса)
            if parent_class is None:
                for child in ast.iter_child_nodes(node):
                    _visit(child, parent_class=None)

        else:
            for child in ast.iter_child_nodes(node):
                _visit(child, parent_class=parent_class)

    for top_node in ast.iter_child_nodes(tree):
        _visit(top_node, parent_class=None)

    return entities


# ──────────────────────── Работа с БД ────────────────────────────────────────

def init_db(db_path: str) -> sqlite3.Connection:
    """Создать/открыть базу данных и применить схему."""
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    conn.executescript(SCHEMA_SQL)
    conn.commit()
    return conn


def index_file(conn: sqlite3.Connection, filepath: str) -> int:
    """
    Проиндексировать один .py-файл.

    Возвращает количество извлечённых сущностей.
    """
    path = Path(filepath).resolve()
    filename = path.name

    # Upsert файла (обновляем если уже есть)
    conn.execute(
        """
        INSERT INTO files (filename, filepath)
        VALUES (?, ?)
        ON CONFLICT(filename) DO UPDATE SET
            filepath   = excluded.filepath,
            indexed_at = CURRENT_TIMESTAMP
        """,
        (filename, str(path)),
    )
    file_id = conn.execute(
        "SELECT id FROM files WHERE filename = ?", (filename,)
    ).fetchone()["id"]

    # Удаляем старые записи для этого файла
    conn.execute("DELETE FROM entities WHERE file_id = ?", (file_id,))

    entities = extract_entities(str(path))
    conn.executemany(
        """
        INSERT INTO entities (file_id, name, kind, line_start, line_end, docstring, parent)
        VALUES (:file_id, :name, :kind, :line_start, :line_end, :docstring, :parent)
        """,
        [{**e, "file_id": file_id} for e in entities],
    )
    conn.commit()
    return len(entities)


def index_directory(db_path: str, source_dir: str) -> None:
    """
    Проиндексировать все .py-файлы в директории рекурсивно.

    Использование:
        python indexer.py ./sample_files
        python indexer.py ./sample_files code_archive.db
    """
    source = Path(source_dir).resolve()
    py_files = sorted(source.rglob("*.py"))

    if not py_files:
        print(f"В директории {source} не найдено .py-файлов", file=sys.stderr)
        return

    print(f"Найдено {len(py_files)} файлов. Индексирую в «{db_path}»...")
    conn = init_db(db_path)

    total_entities = 0
    for py_file in py_files:
        count = index_file(conn, str(py_file))
        total_entities += count
        print(f"  ✓ {py_file.name:40s} → {count} сущностей")

    conn.close()
    print(f"\nГотово! Проиндексировано файлов: {len(py_files)}, сущностей: {total_entities}")


# ─────────────────────────────── CLI ─────────────────────────────────────────

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Использование: python indexer.py <директория> [путь_к_бд.db]")
        sys.exit(1)

    source_dir = sys.argv[1]
    db_path    = sys.argv[2] if len(sys.argv) > 2 else "code_archive.db"

    index_directory(db_path, source_dir)

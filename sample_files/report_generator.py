"""Генератор отчётов в различных форматах."""
import csv
import io
import json
from typing import List, Dict, Any


class ReportGenerator:
    """Генератор отчётов с поддержкой CSV и JSON форматов."""

    def __init__(self, title: str):
        """Инициализация генератора с заголовком отчёта."""
        self.title = title
        self._rows: List[Dict[str, Any]] = []

    def add_row(self, row: Dict[str, Any]) -> None:
        """Добавить строку данных в отчёт."""
        self._rows.append(row)

    def add_rows(self, rows: List[Dict[str, Any]]) -> None:
        """Добавить несколько строк данных в отчёт."""
        self._rows.extend(rows)

    def to_csv(self) -> str:
        """Экспортировать отчёт в формат CSV."""
        if not self._rows:
            return ""
        output = io.StringIO()
        writer = csv.DictWriter(output, fieldnames=self._rows[0].keys())
        writer.writeheader()
        writer.writerows(self._rows)
        return output.getvalue()

    def to_json(self) -> str:
        """Экспортировать отчёт в формат JSON."""
        return json.dumps({
            "title": self.title,
            "count": len(self._rows),
            "data": self._rows
        }, ensure_ascii=False, indent=2)

    def summary(self) -> Dict[str, Any]:
        """Получить краткую сводку по данным отчёта."""
        return {
            "title": self.title,
            "total_rows": len(self._rows),
            "columns": list(self._rows[0].keys()) if self._rows else []
        }

"""Простой поисковый движок с поддержкой полнотекстового поиска."""
import re
from typing import List, Dict, Any


class SearchEngine:
    """Базовый поисковый движок для индексации и поиска документов."""

    def __init__(self):
        """Инициализация поискового индекса."""
        self._index: Dict[str, List[int]] = {}
        self._documents: Dict[int, Dict] = {}
        self._next_id = 0

    def index_document(self, document: Dict[str, Any]) -> int:
        """Добавить документ в поисковый индекс."""
        doc_id = self._next_id
        self._next_id += 1
        self._documents[doc_id] = document
        text = " ".join(str(v) for v in document.values()).lower()
        for token in self._tokenize(text):
            self._index.setdefault(token, []).append(doc_id)
        return doc_id

    def search(self, query: str) -> List[Dict]:
        """Найти документы по поисковому запросу."""
        tokens = self._tokenize(query.lower())
        if not tokens:
            return []
        results = None
        for token in tokens:
            ids = set(self._index.get(token, []))
            results = ids if results is None else results & ids
        return [self._documents[i] for i in (results or [])]

    def _tokenize(self, text: str) -> List[str]:
        """Разбить текст на токены для индексации."""
        return re.findall(r"[a-zа-яё]+", text)

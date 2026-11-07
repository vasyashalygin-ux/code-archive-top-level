"""Сервис для работы с файловым хранилищем."""
import os
import shutil
from pathlib import Path
from typing import Optional


class FileStorage:
    """Локальное файловое хранилище для загрузки и хранения файлов."""

    ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif", ".pdf", ".docx"}

    def __init__(self, base_dir: str):
        """Инициализация хранилища с базовой директорией."""
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(parents=True, exist_ok=True)

    def save_file(self, source_path: str, filename: str) -> str:
        """Сохранить файл в хранилище и вернуть его относительный путь."""
        ext = Path(filename).suffix.lower()
        if ext not in self.ALLOWED_EXTENSIONS:
            raise ValueError(f"Недопустимое расширение файла: {ext}")
        dest = self.base_dir / filename
        shutil.copy2(source_path, dest)
        return str(dest)

    def delete_file(self, filename: str) -> bool:
        """Удалить файл из хранилища."""
        target = self.base_dir / filename
        if target.exists():
            target.unlink()
            return True
        return False

    def get_file_path(self, filename: str) -> Optional[str]:
        """Получить полный путь к файлу в хранилище."""
        target = self.base_dir / filename
        return str(target) if target.exists() else None

    def list_files(self, extension: Optional[str] = None):
        """Получить список всех файлов в хранилище."""
        files = list(self.base_dir.iterdir())
        if extension:
            files = [f for f in files if f.suffix == extension]
        return [f.name for f in files]

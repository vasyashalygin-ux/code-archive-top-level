"""Базовый HTTP-клиент для взаимодействия с внешними API."""
import urllib.request
import urllib.error
import json
from typing import Optional, Dict, Any


class ApiClient:
    """Базовый клиент для HTTP-запросов к REST API."""

    def __init__(self, base_url: str, api_key: Optional[str] = None, timeout: int = 30):
        """Инициализация клиента с базовым URL и опциональным ключом API."""
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.timeout = timeout

    def get(self, path: str, params: Dict = None) -> Dict[str, Any]:
        """Выполнить GET-запрос к API."""
        url = f"{self.base_url}/{path.lstrip('/')}"
        if params:
            query = "&".join(f"{k}={v}" for k, v in params.items())
            url = f"{url}?{query}"
        return self._request("GET", url)

    def post(self, path: str, data: Dict) -> Dict[str, Any]:
        """Выполнить POST-запрос к API с JSON-телом."""
        url = f"{self.base_url}/{path.lstrip('/')}"
        return self._request("POST", url, data)

    def _request(self, method: str, url: str, data: Dict = None) -> Dict[str, Any]:
        """Внутренний метод для выполнения HTTP-запроса."""
        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        body = json.dumps(data).encode() if data else None
        req = urllib.request.Request(url, data=body, headers=headers, method=method)
        try:
            with urllib.request.urlopen(req, timeout=self.timeout) as resp:
                return json.loads(resp.read().decode())
        except urllib.error.HTTPError as e:
            raise RuntimeError(f"API вернул ошибку {e.code}: {e.reason}")

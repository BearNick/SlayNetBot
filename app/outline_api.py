# Minimal Outline Manager API client (apiUrl already includes the secret path)
import httpx
from typing import Optional

class OutlineAPI:
    def __init__(self, base_url: str, api_key: Optional[str] = None):
        # Принимаем полный apiUrl вида:
        # https://IP:PORT/SECRET
        # Никаких ?apiKey= не используем.
        self.base_url = base_url.rstrip("/")  # без завершающего "/"
        self.client = httpx.AsyncClient(verify=False, timeout=15.0)

    def _join(self, path: str) -> str:
        # Склеиваем безопасно: <base>/<path>
        return f"{self.base_url}/{path.lstrip('/')}"

    async def _get(self, path: str):
        url = self._join(path)
        r = await self.client.get(url)
        r.raise_for_status()
        return r.json()

    async def _post(self, path: str, json_body=None):
        url = self._join(path)
        r = await self.client.post(url, json=json_body or {})
        r.raise_for_status()
        return r.json() if r.content else {}

    async def _put(self, path: str, json_body=None):
        url = self._join(path)
        r = await self.client.put(url, json=json_body or {})
        r.raise_for_status()
        return r.json() if r.content else {}

    async def _delete(self, path: str):
        url = self._join(path)
        r = await self.client.delete(url)
        r.raise_for_status()
        return {}

    # Keys
    async def create_key(self, name: str) -> dict:
        return await self._post("access-keys", {"name": name})

    async def set_key_data_limit(self, key_id: str, bytes_limit: int):
        return await self._put(f"access-keys/{key_id}/data-limit", {"limit": {"bytes": bytes_limit}})

    async def delete_key(self, key_id: str):
        return await self._delete(f"access-keys/{key_id}")

    async def list_keys(self) -> dict:
        return await self._get("access-keys")

    async def close(self):
        await self.client.aclose()
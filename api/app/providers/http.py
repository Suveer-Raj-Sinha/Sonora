import httpx
from app.config import settings

def client() -> httpx.AsyncClient:
    return httpx.AsyncClient(timeout=settings.http_timeout_seconds, headers={
        "User-Agent": "SONORA/1.0 (music discovery app; contact: dev@example.com)"
    })

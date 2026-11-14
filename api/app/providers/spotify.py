import base64
import time
from app.config import settings
from app.providers.http import client

_token: tuple[str, float] | None = None

async def access_token() -> str | None:
    global _token
    if not settings.spotify_client_id or not settings.spotify_client_secret:
        return None
    if _token and _token[1] > time.time() + 30:
        return _token[0]
    raw = f"{settings.spotify_client_id}:{settings.spotify_client_secret}".encode()
    auth = base64.b64encode(raw).decode()
    async with client() as c:
        r = await c.post("https://accounts.spotify.com/api/token",
            data={"grant_type": "client_credentials"},
            headers={"Authorization": f"Basic {auth}"})
        r.raise_for_status()
        data = r.json()
        _token = (data["access_token"], time.time() + data.get("expires_in", 3600))
        return _token[0]

async def search_tracks(query: str) -> list[dict]:
    token = await access_token()
    if not token:
        return []
    async with client() as c:
        r = await c.get("https://api.spotify.com/v1/search",
            params={"q": query, "type": "track", "limit": 10},
            headers={"Authorization": f"Bearer {token}"})
        r.raise_for_status()
        return r.json().get("tracks", {}).get("items", [])

async def search_artists(query: str) -> list[dict]:
    token = await access_token()
    if not token:
        return []
    async with client() as c:
        r = await c.get("https://api.spotify.com/v1/search",
            params={"q": query, "type": "artist", "limit": 6},
            headers={"Authorization": f"Bearer {token}"})
        r.raise_for_status()
        return r.json().get("artists", {}).get("items", [])

from app.config import settings
from app.providers.http import client

async def youtube_search(title: str, artist: str):
    if not settings.youtube_api_key:
        return None
    async with client() as c:
        r = await c.get("https://www.googleapis.com/youtube/v3/search", params={
            "part": "snippet", "q": f"{artist} {title} official audio",
            "type": "video", "videoCategoryId": "10", "maxResults": 1,
            "key": settings.youtube_api_key
        })
        r.raise_for_status()
        items = r.json().get("items", [])
        if not items: return None
        vid = items[0]["id"]["videoId"]
        return {"provider": "youtube", "playable": True,
                "url": f"https://www.youtube.com/watch?v={vid}",
                "embed_url": f"https://www.youtube.com/embed/{vid}",
                "external_id": vid, "title": items[0]["snippet"]["title"]}

async def jamendo_search(title: str, artist: str):
    if not settings.jamendo_client_id:
        return None
    async with client() as c:
        r = await c.get("https://api.jamendo.com/v3.0/tracks/", params={
            "client_id": settings.jamendo_client_id, "format": "json",
            "limit": 1, "namesearch": f"{artist} {title}",
            "audioformat": "mp32"
        })
        r.raise_for_status()
        results = r.json().get("results", [])
        if not results: return None
        item = results[0]
        return {"provider": "jamendo", "playable": True,
                "url": item.get("shareurl"), "external_id": item.get("id"),
                "title": item.get("name")}

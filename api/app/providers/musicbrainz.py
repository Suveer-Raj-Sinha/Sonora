from app.providers.http import client

async def search_recordings(query: str) -> list[dict]:
    async with client() as c:
        r = await c.get("https://musicbrainz.org/ws/2/recording/", params={
            "query": query, "fmt": "json", "limit": 8
        })
        r.raise_for_status()
        return r.json().get("recordings", [])

async def search_artists(query: str) -> list[dict]:
    async with client() as c:
        r = await c.get("https://musicbrainz.org/ws/2/artist/", params={
            "query": query, "fmt": "json", "limit": 6
        })
        r.raise_for_status()
        return r.json().get("artists", [])

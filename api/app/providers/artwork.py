from app.providers.http import client

async def cover_art(mbid: str) -> str | None:
    async with client() as c:
        r = await c.get(f"https://coverartarchive.org/release/{mbid}")
        if r.status_code != 200:
            return None
        data = r.json()
        images = data.get("images", [])
        if not images:
            return None
        return images[0].get("image")

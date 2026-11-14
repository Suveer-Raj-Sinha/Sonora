from app.providers.http import client

async def find_lyrics(title: str, artist: str, album: str | None = None, duration: int | None = None):
    params = {"track_name": title, "artist_name": artist}
    if album: params["album_name"] = album
    if duration: params["duration"] = round(duration / 1000)
    async with client() as c:
        r = await c.get("https://lrclib.net/api/get", params=params)
        if r.status_code == 404:
            return None
        r.raise_for_status()
        return r.json()

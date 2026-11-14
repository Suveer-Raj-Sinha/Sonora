import asyncio, hashlib, re
from app.catalog import SONGS, cache
from app.models import Song
from app.providers import spotify, musicbrainz

def slug_id(title: str, artist: str) -> str:
    raw = re.sub(r"[^a-z0-9]+", "-", f"{title}-{artist}".lower()).strip("-")
    return raw[:70] or hashlib.md5(f"{title}{artist}".encode()).hexdigest()[:12]

def normalize_spotify(item: dict) -> Song:
    artists = [a["name"] for a in item.get("artists", [])]
    album = item.get("album", {})
    images = album.get("images", [])
    return Song(id=slug_id(item.get("name", ""), ", ".join(artists)),
        title=item.get("name", "Unknown"), artists=artists,
        album=album.get("name"), duration_ms=item.get("duration_ms"),
        release_date=album.get("release_date"),
        artwork_url=images[0]["url"] if images else None,
        artwork_source="Spotify" if images else None,
        isrc=item.get("external_ids", {}).get("isrc"),
        explicit=item.get("explicit"), popularity=item.get("popularity"),
        source_ids={"spotify": item.get("id", "")},
        provenance={"metadata": "Spotify", "confidence": "provider-match"})

def normalize_mb(item: dict) -> Song:
    credits = item.get("artist-credit", [])
    artists = [x.get("name", "") for x in credits if isinstance(x, dict)]
    length = item.get("length")
    return Song(id=slug_id(item.get("title", ""), ", ".join(artists)),
        title=item.get("title", "Unknown"), artists=artists or ["Unknown artist"],
        duration_ms=length, source_ids={"musicbrainz": item.get("id", "")},
        provenance={"metadata": "MusicBrainz", "confidence": "recording-match"})

async def search_songs(q: str) -> list[Song]:
    key = f"search:{q.lower()}"
    cached = cache.get(key)
    if cached is not None: return cached
    spotify_task = spotify.search_tracks(q)
    mb_task = musicbrainz.search_recordings(q)
    results = await asyncio.gather(spotify_task, mb_task, return_exceptions=True)
    out: list[Song] = []
    seen = set()
    if not isinstance(results[0], Exception):
        for raw in results[0]:
            song = normalize_spotify(raw)
            signature = (song.title.lower(), tuple(x.lower() for x in song.artists))
            if signature not in seen:
                seen.add(signature); out.append(song)
    if not isinstance(results[1], Exception):
        for raw in results[1]:
            song = normalize_mb(raw)
            signature = (song.title.lower(), tuple(x.lower() for x in song.artists))
            if signature not in seen:
                seen.add(signature); out.append(song)
    for song in SONGS.values():
        if q.lower() in song.title.lower() or any(q.lower() in a.lower() for a in song.artists):
            signature = (song.title.lower(), tuple(x.lower() for x in song.artists))
            if signature not in seen:
                seen.add(signature); out.append(song)
    # Persist normalized provider hits in the process catalog so detail/playback routes can resolve them.
    for song in out:
        SONGS.setdefault(song.id, song)
    cache.set(key, out)
    return out

async def search_artists(q: str) -> list[dict]:
    a, b = await asyncio.gather(spotify.search_artists(q), musicbrainz.search_artists(q), return_exceptions=True)
    out = []
    if not isinstance(a, Exception):
        out += [{"id": x["id"], "name": x["name"], "source": "spotify"} for x in a]
    if not isinstance(b, Exception):
        out += [{"id": x["id"], "name": x["name"], "source": "musicbrainz"} for x in b]
    return out

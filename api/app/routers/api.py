import uuid, random
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from app.catalog import SONGS, get_song, all_songs
from app.models import Song, Lyrics, PlaybackOption
from app.services.music import search_songs, search_artists
from app.services.appearance import appearance
from app.services.discovery import filter_songs
from app.providers.lyrics import find_lyrics
from app.providers.playback import youtube_search, jamendo_search

router = APIRouter()
SESSIONS: dict[str, dict] = {}

@router.get("/health")
async def health():
    return {"status": "ok", "service": "sonora-api", "version": "1.0.0"}

@router.get("/providers")
async def providers():
    from app.config import settings
    return {"metadata": ["spotify" if settings.spotify_client_id else "spotify (not configured)", "musicbrainz"],
        "lyrics": ["lrclib"], "artwork": ["cover-art-archive"],
        "playback": {"primary": "youtube", "fallback": "jamendo"},
        "configured": {"spotify": bool(settings.spotify_client_id), "youtube": bool(settings.youtube_api_key),
                       "jamendo": bool(settings.jamendo_client_id)}}

@router.get("/search")
async def search(q: str = Query(min_length=1), type: str = "all"):
    if type in ("all", "songs", "suggestions"):
        songs = await search_songs(q)
        if type == "songs": return {"items": songs, "count": len(songs)}
        if type == "suggestions": return {"items": [s.title for s in songs[:8]]}
        artists = await search_artists(q)
        return {"songs": songs, "artists": artists, "albums": [], "count": len(songs)+len(artists)}
    if type == "artists":
        items = await search_artists(q); return {"items": items, "count": len(items)}
    if type == "albums":
        return {"items": [], "count": 0, "note": "Album aggregation is reserved for the next provider adapter."}
    raise HTTPException(400, "type must be all, songs, artists, albums or suggestions")

@router.get("/songs")
async def songs(q: str | None = None, genre: str | None = None, mood: str | None = None,
                era: str | None = None, language: str | None = None, limit: int = 20, offset: int = 0):
    items = await search_songs(q) if q else filter_songs(genre, mood, era, language)
    return {"items": items[offset:offset+min(limit,100)], "count": len(items), "limit": limit, "offset": offset}

@router.get("/songs/random")
async def random_song():
    items = all_songs()
    if not items: raise HTTPException(404, "Catalog is empty")
    return random.choice(items)

@router.get("/songs/{song_id}", response_model=Song)
async def song_detail(song_id: str):
    item = get_song(song_id)
    if not item: raise HTTPException(404, "Song not found in SONORA catalog")
    return item

@router.get("/songs/{song_id}/appearance")
async def song_appearance(song_id: str):
    item = get_song(song_id)
    if not item: raise HTTPException(404, "Song not found")
    return appearance(item)

@router.get("/songs/{song_id}/lyrics", response_model=Lyrics)
async def lyrics(song_id: str):
    item = get_song(song_id)
    if not item: raise HTTPException(404, "Song not found")
    result = await find_lyrics(item.title, item.artists[0], item.album, item.duration_ms)
    if not result:
        return Lyrics(song_id=song_id, available=False)
    text = result.get("syncedLyrics") or result.get("plainLyrics")
    return Lyrics(song_id=song_id, lyrics=text, synced=bool(result.get("syncedLyrics")),
        source="LRCLIB", instrumental=bool(result.get("instrumental")), available=bool(text))

async def playback_options(item):
    primary = await youtube_search(item.title, item.artists[0])
    if primary:
        return [PlaybackOption(**primary)]
    fallback = await jamendo_search(item.title, item.artists[0])
    if fallback:
        return [PlaybackOption(**fallback)]
    return []

@router.get("/songs/{song_id}/playback")
async def playback(song_id: str):
    item = get_song(song_id)
    if not item: raise HTTPException(404, "Song not found")
    options = await playback_options(item)
    return {"song_id": song_id, "provider_policy": "youtube_primary_jamendo_fallback",
            "available": bool(options), "options": options}

class SessionRequest(BaseModel):
    song_id: str

@router.post("/playback/sessions")
async def create_session(body: SessionRequest):
    item = get_song(body.song_id)
    if not item: raise HTTPException(404, "Song not found")
    options = await playback_options(item)
    if not options: raise HTTPException(503, "No permitted playback provider result available")
    sid = str(uuid.uuid4())
    SESSIONS[sid] = {"song_id": body.song_id, "provider": options[0].provider}
    return {"session_id": sid, "song_id": body.song_id, "playback": options[0]}

@router.post("/playback/sessions/{session_id}/fallback")
async def fallback(session_id: str):
    session = SESSIONS.get(session_id)
    if not session: raise HTTPException(404, "Session not found")
    item = get_song(session["song_id"])
    if not item: raise HTTPException(404, "Song not found")
    alt = await jamendo_search(item.title, item.artists[0]) if session["provider"] == "youtube" else await youtube_search(item.title, item.artists[0])
    if not alt: raise HTTPException(503, "No fallback provider result available")
    session["provider"] = alt["provider"]
    return {"session_id": session_id, "playback": PlaybackOption(**alt)}

class PlaybackReport(BaseModel):
    session_id: str
    provider: str
    event: str
    details: dict = {}

@router.post("/playback/report")
async def playback_report(body: PlaybackReport):
    if body.session_id not in SESSIONS: raise HTTPException(404, "Session not found")
    return {"received": True, "event": body.event, "message": "Report accepted for this API process."}

@router.get("/discover")
async def discover(genre: str | None = None, mood: str | None = None,
                   era: str | None = None, language: str | None = None, limit: int = 20):
    items = filter_songs(genre, mood, era, language)
    return {"items": items[:min(limit,100)], "count": len(items), "mode": "hybrid-catalog"}

@router.get("/discover/daily")
async def daily_discovery():
    items = sorted(all_songs(), key=lambda x: x.id)
    return {"date": __import__("datetime").date.today().isoformat(), "items": items[:5],
            "algorithm": "deterministic-demo-rotation"}

@router.get("/songs/{song_id}/similar")
async def similar(song_id: str, limit: int = 10):
    item = get_song(song_id)
    if not item: raise HTTPException(404, "Song not found")
    pool = [s for s in all_songs() if s.id != song_id]
    scored = sorted(pool, key=lambda s: len(set(item.genres+s.moods) & set(s.genres+s.moods)), reverse=True)
    return {"items": scored[:min(limit,50)], "count": min(limit,len(scored))}

@router.get("/filters")
async def filters():
    songs = all_songs()
    def values(field):
        return sorted({v for s in songs for v in getattr(s, field) if v})
    return {"genres": values("genres"), "moods": values("moods"),
            "eras": sorted({s.era for s in songs if s.era}),
            "languages": sorted({s.language for s in songs if s.language})}

@router.get("/collections/{collection_id}")
async def collection(collection_id: str):
    if collection_id == "featured":
        return {"id": collection_id, "title": "SONORA Featured", "items": all_songs()}
    raise HTTPException(404, "Collection not found")

@router.get("/artists/{artist_id}")
async def artist_detail(artist_id: str):
    matches = [s for s in all_songs() if any(artist_id.lower() in a.lower() for a in s.artists)]
    if not matches: raise HTTPException(404, "Artist not found in catalog")
    return {"id": artist_id, "name": matches[0].artists[0], "songs": matches}

@router.get("/albums/{album_id}")
async def album_detail(album_id: str):
    matches = [s for s in all_songs() if s.album and album_id.lower() in s.album.lower()]
    if not matches: raise HTTPException(404, "Album not found in catalog")
    return {"id": album_id, "title": matches[0].album, "songs": matches}

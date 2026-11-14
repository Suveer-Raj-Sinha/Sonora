from app.models import Song
from app.cache import TTLCache
from app.config import settings

cache = TTLCache(settings.cache_ttl_seconds)
SONGS: dict[str, Song] = {
    "demo-midnight-city": Song(
        id="demo-midnight-city", title="Midnight City", artists=["M83"],
        album="Hurry Up, We're Dreaming", duration_ms=244000, genres=["synth-pop", "electronic"],
        moods=["dreamy", "energetic", "nostalgic"], era="2010s", language="English",
        provenance={"catalog": "SONORA demo seed"}, popularity=88
    ),
    "demo-space-song": Song(
        id="demo-space-song", title="Space Song", artists=["Beach House"],
        album="Depression Cherry", duration_ms=320000, genres=["dream pop", "indie"],
        moods=["dreamy", "melancholic", "calm"], era="2010s", language="English",
        provenance={"catalog": "SONORA demo seed"}, popularity=91
    ),
    "demo-sunset-lover": Song(
        id="demo-sunset-lover", title="Sunset Lover", artists=["Petit Biscuit"],
        album="Presence", duration_ms=237000, genres=["electronic", "chill"],
        moods=["warm", "calm", "uplifting"], era="2010s", language="Instrumental",
        provenance={"catalog": "SONORA demo seed"}, popularity=82
    ),
}

def get_song(song_id: str) -> Song | None:
    return SONGS.get(song_id)

def all_songs() -> list[Song]:
    return list(SONGS.values())

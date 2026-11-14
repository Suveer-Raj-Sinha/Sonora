from typing import Any
from pydantic import BaseModel, Field

class Artist(BaseModel):
    id: str
    name: str
    genres: list[str] = []
    image_url: str | None = None
    source_ids: dict[str, str] = {}

class Album(BaseModel):
    id: str
    title: str
    artist_names: list[str] = []
    release_date: str | None = None
    image_url: str | None = None
    source_ids: dict[str, str] = {}

class Song(BaseModel):
    id: str
    title: str
    artists: list[str]
    album: str | None = None
    duration_ms: int | None = None
    release_date: str | None = None
    genres: list[str] = []
    moods: list[str] = []
    language: str | None = None
    era: str | None = None
    isrc: str | None = None
    explicit: bool | None = None
    artwork_url: str | None = None
    artwork_source: str | None = None
    source_ids: dict[str, str] = {}
    provenance: dict[str, Any] = {}
    popularity: float | None = None

class Lyrics(BaseModel):
    song_id: str
    lyrics: str | None = None
    synced: bool = False
    source: str | None = None
    instrumental: bool = False
    available: bool = False

class PlaybackOption(BaseModel):
    provider: str
    playable: bool
    url: str | None = None
    embed_url: str | None = None
    external_id: str | None = None
    title: str | None = None
    instructions: str = "Open the provider playback surface."
    capabilities: dict[str, bool] = {"seek": False, "volume": False, "autoplay": False}

class BookAppearance(BaseModel):
    song_id: str
    source: str
    dominant_color: str
    palette: list[str]
    pattern: str
    theme: str
    dimensions: dict[str, float]
    attribution: str | None = None
    frontend_rendering: bool = True

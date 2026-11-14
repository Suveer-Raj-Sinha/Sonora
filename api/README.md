# SONORA API

A FastAPI backend for SONORA's music discovery and book-inspired listening experience.

## Stack
- FastAPI + async HTTPX
- Spotify Web API and MusicBrainz metadata adapters (parallel lookup)
- LRCLIB lyrics
- Cover Art Archive artwork lookup
- YouTube primary / Jamendo fallback playback discovery
- In-memory catalog and TTL cache; database intentionally deferred

## Run locally
```bash
python -m venv .venv
# Windows PowerShell:
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
copy .env.example .env
uvicorn app.main:app --reload
```
Open `http://127.0.0.1:8000/docs`.

## Configuration
Spotify credentials enable Spotify metadata enrichment. YouTube and Jamendo credentials enable their respective playback adapters. MusicBrainz and LRCLIB can be queried without credentials; use a descriptive User-Agent in production. Missing credentials/providers degrade gracefully.

## API
All versioned routes use `/api/v1`.
- `GET /health`, `GET /api/v1/health`, `GET /api/v1/providers`
- `GET /api/v1/search?q=...&type=all|songs|artists|albums|suggestions`
- `GET /api/v1/songs`, `GET /api/v1/songs/{song_id}`, `GET /api/v1/songs/random`
- `GET /api/v1/songs/{song_id}/lyrics`
- `GET /api/v1/songs/{song_id}/playback`
- `POST /api/v1/playback/sessions`, `POST /api/v1/playback/sessions/{session_id}/fallback`
- `POST /api/v1/playback/report`
- `GET /api/v1/songs/{song_id}/appearance`
- `GET /api/v1/artists/{artist_id}`, `GET /api/v1/albums/{album_id}`
- `GET /api/v1/discover`, `GET /api/v1/discover/daily`, `GET /api/v1/songs/{song_id}/similar`
- `GET /api/v1/filters`, `GET /api/v1/collections/{collection_id}`

## Important provider behavior
SONORA normalizes provider results into internal IDs and retains provider provenance. Matching prioritizes ISRC/recording identifiers, then title + artist + album + duration. Live, remix and alternate recordings are not silently merged. Playback discovery returns provider-specific playable references/instructions, not an unrestricted scraped audio URL. Provider availability and rights vary by region and track.

## Artwork policy
Artwork is used only when the source/provider makes it available for the intended use. When usable artwork is unavailable or restricted, the API creates a deterministic theme from genre, mood, era and language. The frontend should render the book visuals; this API returns appearance tokens and source attribution.

## Current implementation boundary
This is a runnable V1 backend foundation with working provider adapters, normalized schemas, graceful fallbacks, API routes and in-memory demo catalog. Live provider results require valid credentials where applicable, and provider terms/permissions must be respected. Persistence, user accounts, personal libraries and production-grade distributed caching are intentionally deferred.

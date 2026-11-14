import hashlib
from app.models import Song, BookAppearance

PALETTES = {
    "dreamy": ["#829DBB", "#C7D2DC", "#E8DCCB"],
    "melancholic": ["#53677E", "#8795A5", "#D0C9C0"],
    "energetic": ["#F26B38", "#F2B544", "#252B42"],
    "calm": ["#789B91", "#C5D8CB", "#E9E2D5"],
    "warm": ["#C8794B", "#E2B77D", "#5C4650"],
    "default": ["#64748B", "#CBD5E1", "#1E293B"],
}

def appearance(song: Song) -> BookAppearance:
    # Artwork is returned only when supplied by a source; frontend must honor source terms.
    source = "artwork" if song.artwork_url else "metadata-fallback"
    tags = [x.lower() for x in song.moods + song.genres]
    mood = next((x for x in ["dreamy", "melancholic", "energetic", "calm", "warm"] if x in tags), "default")
    palette = PALETTES[mood]
    seed = hashlib.sha256(song.id.encode()).hexdigest()
    patterns = ["orbital", "waveform", "petal", "grain-free geometric", "starfield"]
    pattern = patterns[int(seed[:4], 16) % len(patterns)]
    seconds = (song.duration_ms or 180000) / 1000
    width = round(0.72 + min(seconds, 600) / 3000, 3)
    return BookAppearance(song_id=song.id, source=source,
        dominant_color=palette[0], palette=palette, pattern=pattern,
        theme=mood, dimensions={"width": width, "height": 1.0},
        attribution=song.artwork_source)

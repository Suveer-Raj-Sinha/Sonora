from app.catalog import all_songs
from app.models import Song

def filter_songs(genre=None, mood=None, era=None, language=None):
    songs = all_songs()
    if genre: songs = [s for s in songs if genre.lower() in [x.lower() for x in s.genres]]
    if mood: songs = [s for s in songs if mood.lower() in [x.lower() for x in s.moods]]
    if era: songs = [s for s in songs if s.era and era.lower() in s.era.lower()]
    if language: songs = [s for s in songs if s.language and language.lower() in s.language.lower()]
    return songs

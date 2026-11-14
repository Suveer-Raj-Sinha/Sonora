from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    app_name: str = "SONORA API"
    app_version: str = "1.0.0"
    api_prefix: str = "/api/v1"
    environment: str = "development"
    spotify_client_id: str = ""
    spotify_client_secret: str = ""
    youtube_api_key: str = ""
    jamendo_client_id: str = ""
    cache_ttl_seconds: int = 900
    http_timeout_seconds: float = 12.0
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()

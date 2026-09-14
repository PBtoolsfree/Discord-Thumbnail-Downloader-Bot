from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict
import os

class Settings(BaseSettings):
    # Discord Configuration
    discord_token: str = ""
    discord_client_id: str = ""
    discord_guild_id: str = ""
    thumbnail_channel_id: str = ""

    # Limits & Features
    max_urls_per_message: int = 5
    max_image_size_mb: int = 8
    cache_ttl_hours: int = 24
    max_concurrent_downloads: int = 3
    request_timeout: int = 15

    # Logging
    log_level: str = "INFO"
    
    # Setup UI
    setup_enabled: bool = True
    setup_password: str = "change_this_default_password"
    setup_port: int = 8080

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

def get_settings() -> Settings:
    return Settings()

settings = get_settings()

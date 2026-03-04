"""app/config.py — Persistence Service configuration."""

from pydantic_settings import BaseSettings


class PersistenceSettings(BaseSettings):
    service_port: int = 8004
    app_env: str = "development"
    log_level: str = "debug"

    auth_service_url: str = "http://auth-service:8001"
    database_url: str = "sqlite+aiosqlite:///./data/whiteboard.db"

    class Config:
        env_file = ".env"


settings = PersistenceSettings()

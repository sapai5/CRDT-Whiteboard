"""app/config.py — CRDT Sync Service configuration."""

from pydantic_settings import BaseSettings


class SyncSettings(BaseSettings):
    service_port: int = 8003
    app_env: str = "development"
    log_level: str = "debug"

    auth_service_url: str = "http://auth-service:8001"
    room_service_url: str = "http://room-service:8002"
    persistence_service_url: str = "http://persistence-service:8004"

    max_connections_per_room: int = 50
    crdt_snapshot_interval_seconds: int = 30

    class Config:
        env_file = ".env"


settings = SyncSettings()

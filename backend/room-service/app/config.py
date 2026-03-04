"""app/config.py — Room Service configuration."""

from pydantic_settings import BaseSettings


class RoomSettings(BaseSettings):
    service_port: int = 8002
    app_env: str = "development"
    log_level: str = "debug"
    auth_service_url: str = "http://auth-service:8001"

    class Config:
        env_file = ".env"


settings = RoomSettings()

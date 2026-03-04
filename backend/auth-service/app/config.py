"""app/config.py — Auth Service configuration."""

from pydantic_settings import BaseSettings


class AuthSettings(BaseSettings):
    service_port: int = 8001
    app_env: str = "development"
    log_level: str = "debug"

    jwt_secret: str = "change-me-in-production"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 60
    refresh_token_expire_days: int = 30

    class Config:
        env_file = ".env"


settings = AuthSettings()

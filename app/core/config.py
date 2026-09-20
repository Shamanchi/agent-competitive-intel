"""Настройки приложения через pydantic-settings."""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    price_alert_pct: float = 5.0
    news_spike_mult: float = 2.0
    app_host: str = "0.0.0.0"
    app_port: int = 8000


_settings: Settings | None = None


def get_settings() -> Settings:
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings

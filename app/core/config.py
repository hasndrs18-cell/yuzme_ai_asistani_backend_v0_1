from functools import lru_cache

from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Yüzme AI Asistanı"
    environment: str = "development"
    log_level: str = "INFO"
    llm_provider: str = "mock"
    llm_api_key: str = ""
    llm_base_url: str = "https://api.openai.com/v1"
    llm_model: str = "gpt-4o-mini"
    llm_timeout_seconds: float = 20.0
    research_provider: str = "none"
    research_api_key: str = ""
    research_timeout_seconds: float = 4.0
    research_max_results: int = 5
    stt_provider: str = "mock"
    tts_provider: str = "mock"
    auth_secret: str = "development-only-change-me"
    auth_issuer: str = "yuzme-ai-asistani"
    auth_audience: str = "yuzme-ai-client"
    auth_token_lifetime_seconds: int = 900
    websocket_auth_timeout_seconds: float = 5.0
    google_client_id: str = ""
    google_client_secret: str = ""
    google_redirect_uri: str = "http://localhost:8000/api/v1/auth/google/callback"
    frontend_url: str = "http://localhost:3000"
    frontend_urls: str = ""

    redis_url: str = "redis://localhost:6379/0"
    database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/yuzme_ai_db"
    postgres_dsn: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/yuzme_ai_db"
    checkpoint_provider: str = "redis"
    db_pool_min_size: int = 2
    db_pool_max_size: int = 10
    repository_backend: str = "postgres"

    model_config = SettingsConfigDict(env_file=".env", case_sensitive=False, extra="ignore")

    @model_validator(mode="after")
    def reject_default_production_secret(self) -> "Settings":
        if self.environment.lower() == "production" and self.auth_secret == "development-only-change-me":
            raise ValueError("AUTH_SECRET must be changed in production")
        return self


@lru_cache

def get_settings() -> Settings:
    return Settings()

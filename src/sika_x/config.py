import os
from dataclasses import dataclass, field

from dotenv import load_dotenv


@dataclass(frozen=True)
class Settings:
    app_env: str
    log_level: str
    timezone: str
    database_url: str
    llm_provider: str
    llm_model: str
    llm_api_key: str = field(default="", repr=False)


def load_settings(use_dotenv: bool = True) -> Settings:
    """Load configuration from environment variables (and .env if enabled)."""
    if use_dotenv:
        load_dotenv()
    return Settings(
        app_env=os.getenv("APP_ENV", "dev"),
        log_level=os.getenv("LOG_LEVEL", "INFO"),
        timezone=os.getenv("TIMEZONE", "Africa/Accra"),
        database_url=os.getenv("DATABASE_URL", "sqlite:///./sika_x.db"),
        llm_provider=os.getenv("LLM_PROVIDER", "mock"),
        llm_model=os.getenv("LLM_MODEL", "gemini-4-hydrogen"),
        llm_api_key=os.getenv("LLM_API_KEY", ""),
    )

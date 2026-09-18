"""Application configuration."""

from pydantic import ConfigDict
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings from environment variables."""

    model_config = ConfigDict(env_file=".env")

    swisscom_api_key: str
    swisscom_base_url: str = (
        "https://api.swisscom.com/products/swiss-ai-weeks/apertus-1.5-70b/v1"
    )
    swisscom_model: str = "swiss-ai/Apertus-v1.5-70B"
    log_level: str = "INFO"


def get_settings() -> Settings:
    """Get or create settings instance."""
    return Settings()

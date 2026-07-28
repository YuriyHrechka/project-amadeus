from typing import Literal, Optional
from pydantic import computed_field, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

from app.core.llm_config import OpenAISettings


class Settings(BaseSettings):
    """Application configuration, loaded from environment variables and `.env`."""

    # Core settings
    PROJECT_NAME: str = "Project Amadeus"
    VERSION: str = "0.1.0"
    DIVERGENCE_METER: str = "1.048596"
    LOG_LEVEL: str = "INFO"

    # DB settings
    DB_USER: str
    DB_PASSWORD: str
    DB_HOST: str
    DB_PORT: int = 5432
    DB_NAME: str

    # AI settings
    LLM_PROVIDER: Literal["openai"] = "openai"
    openai: Optional[OpenAISettings] = None

    @model_validator(mode="after")
    def validate_active_provider_settings(self) -> "Settings":
        """Ensure the settings block for the selected LLM_PROVIDER was actually provided."""
        provider_settings = getattr(self, self.LLM_PROVIDER, None)

        if provider_settings is None:
            raise ValueError(
                f"LLM_PROVIDER={self.LLM_PROVIDER!r}, but no matching configuration found. "
                f"Set {self.LLM_PROVIDER.upper()}__API_KEY (and optionally "
                f"{self.LLM_PROVIDER.upper()}__MODEL) in your .env file."
            )
        return self

    @computed_field
    @property
    def DATABASE_URL(self) -> str:
        """Build the async PostgreSQL connection string from the individual DB_* fields."""
        return f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

    model_config = SettingsConfigDict(
        env_file=".env", env_nested_delimiter="__", env_file_encoding="utf-8", env_ignore_empty=True, extra="ignore"
    )


settings = Settings()

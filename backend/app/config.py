from functools import lru_cache

from pydantic import AliasChoices, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    openai_api_key: str | None = Field(
        default=None,
        validation_alias=AliasChoices("AZURE_OPENAI_API_KEY", "OPENAI_API_KEY"),
    )
    openai_base_url: str | None = Field(
        default=None,
        validation_alias=AliasChoices("OPENAI_BASE_URL", "AZURE_OPENAI_ENDPOINT"),
    )
    openai_model: str = Field(
        default="gpt-5.4-nano-1",
        validation_alias=AliasChoices("AZURE_OPENAI_MODEL", "OPENAI_MODEL"),
    )
    frontend_origin: str = Field(default="http://localhost:5173", validation_alias="FRONTEND_ORIGIN")
    speech_endpoint: str | None = Field(default=None, validation_alias="AZURE_SPEECH_ENDPOINT")
    speech_resource_id: str | None = Field(default=None, validation_alias="AZURE_RESOURCE_ID")
    speech_voice: str = Field(default="en-US-Grant:MAI-Voice-1", validation_alias="AZURE_SPEECH_VOICE")

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()

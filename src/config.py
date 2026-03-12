import os
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional

class Settings(BaseSettings):
    gemini_api_key: Optional[str] = None
    anthropic_api_key: Optional[str] = None
    openai_api_key: Optional[str] = None
    openrouter_api_key: Optional[str] = None
    
    debug: bool = True
    port: int = 8000
    
    # Provider mapping configuration
    provider_novice: str = "gemini"
    provider_medium: str = "claude"
    provider_expert: str = "openai"

    # Model selection variables
    novice_model: str = "gemini-3.1-pro-preview"
    medium_model: str = "claude-opus-4.6"
    advanced_model: str = "gpt-5.3-codex"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

settings = Settings()

def validate_config_for_level(level: str):
    """Validates that the required API key for a given level exists."""
    if level == "novice" and not (settings.gemini_api_key or settings.openrouter_api_key):
        raise ValueError("GEMINI_API_KEY or OPENROUTER_API_KEY is required for 'novice' level.")
    if level == "medium" and not (settings.anthropic_api_key or settings.openrouter_api_key):
        raise ValueError("ANTHROPIC_API_KEY or OPENROUTER_API_KEY is required for 'medium' level.")
    if level == "expert" and not (settings.openai_api_key or settings.openrouter_api_key):
        raise ValueError("OPENAI_API_KEY or OPENROUTER_API_KEY is required for 'expert' level.")

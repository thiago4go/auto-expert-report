"""Configuration loading for the Study Guide Generator."""

import os
from pathlib import Path
from typing import Optional

from pydantic import Field, HttpUrl, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class ApiSettings(BaseSettings):
    """API related settings."""

    model_config = SettingsConfigDict(
        env_prefix="PPLX_", env_file=".env", extra="ignore"
    )

    api_key: SecretStr = Field(..., description="Perplexity API Key")
    # Add other API related settings like base URL if needed later
    # base_url: HttpUrl = Field("https://api.perplexity.ai", description="Perplexity API Base URL")


class AppSettings(BaseSettings):
    """Application specific settings."""

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    token_budget_usd: float = Field(
        0.25, description="Maximum token spend in USD per run"
    )
    site_dir: Path = Field(
        "site", description="Output root directory for generated HTML pages"
    )
    template_dir: Path = Field(
        "templates", description="Directory containing Jinja2 templates"
    )
    asset_dir: Path = Field(
        "assets", description="Directory containing static assets (CSS, JS)"
    )
    cache_type: str = Field(
        "memory", description="Cache backend type ('memory' or 'redis')"
    )
    redis_url: Optional[str] = Field(
        None, description="Redis connection URL (if cache_type is 'redis')"
    )


class Settings(BaseSettings):
    """Aggregated settings."""

    api: ApiSettings = ApiSettings()
    app: AppSettings = AppSettings()


# Load settings globally on import
# In a larger app, consider dependency injection
try:
    settings = Settings()
except Exception as e:
    # Provide a more helpful error message if loading fails
    print(f"Error loading configuration: {e}")
    print(
        "Please ensure required environment variables (e.g., PPLX_API_KEY) are set."
    )
    # Re-raise or exit depending on desired behavior
    raise


if __name__ == "__main__":
    # Example of accessing settings
    print("Loaded Configuration:")
    print(f"  API Key: {settings.api.api_key.get_secret_value()[:4]}... (masked)")
    print(f"  Token Budget: ${settings.app.token_budget_usd:.2f}")
    print(f"  Site Directory: {settings.app.site_dir.resolve()}")
    print(f"  Template Directory: {settings.app.template_dir.resolve()}")
    print(f"  Asset Directory: {settings.app.asset_dir.resolve()}")
    print(f"  Cache Type: {settings.app.cache_type}")
    if settings.app.redis_url:
        print(f"  Redis URL: {settings.app.redis_url}")

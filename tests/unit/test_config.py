"""Unit tests for the configuration loading."""

import os
from pathlib import Path
from unittest.mock import patch

import pytest
from pydantic import ValidationError
from pydantic_settings import SettingsConfigDict

# Import the module that loads settings to potentially reload it
from studyguide import config


# Use monkeypatch fixture for setting/unsetting environment variables safely
@pytest.fixture(autouse=True)
def manage_environment(monkeypatch):
    """Fixture to clean up environment variables after each test."""
    original_env = os.environ.copy()
    yield monkeypatch  # Provide the monkeypatch fixture to the test
    # Restore original environment variables after test execution
    os.environ.clear()
    os.environ.update(original_env)


def reload_settings(monkeypatch):
    """Helper function to reload settings based on current environment."""
    # Temporarily remove the loaded settings instance if it exists
    if "settings" in config.__dict__:
        del config.settings

    # Need to reload the module to re-trigger settings loading
    # This is a bit tricky; patching BaseSettings might be cleaner in complex cases
    # For now, let's try modifying the environment and re-importing parts or reloading
    # A simpler approach for testing is often to instantiate Settings directly
    # rather than relying on the module-level instance.

    # Let's instantiate directly for cleaner testing
    class TestApiSettings(config.ApiSettings):
        model_config = SettingsConfigDict(
            env_prefix="PPLX_", extra="ignore"
        )  # No .env file for tests

    class TestAppSettings(config.AppSettings):
        model_config = SettingsConfigDict(extra="ignore")  # No .env file for tests

    class TestSettings(config.Settings):
        api: TestApiSettings = TestApiSettings()
        app: TestAppSettings = TestAppSettings()

    return TestSettings()


def test_load_defaults(monkeypatch):
    """Test loading default settings when environment variables are not set."""
    # PPLX_API_KEY is required, so we must set it
    monkeypatch.setenv("PPLX_API_KEY", "test_key_default")

    settings = reload_settings(monkeypatch)

    assert settings.api.api_key.get_secret_value() == "test_key_default"
    assert settings.app.token_budget_usd == 0.25
    assert settings.app.site_dir == Path("site")
    assert settings.app.template_dir == Path("templates")
    assert settings.app.asset_dir == Path("assets")
    assert settings.app.cache_type == "memory"
    assert settings.app.redis_url is None


def test_load_from_env(monkeypatch):
    """Test loading settings from environment variables."""
    monkeypatch.setenv("PPLX_API_KEY", "actual_api_key_from_env")
    monkeypatch.setenv("TOKEN_BUDGET_USD", "1.50")
    monkeypatch.setenv("SITE_DIR", "/tmp/test_site")
    monkeypatch.setenv("TEMPLATE_DIR", "custom_templates")
    monkeypatch.setenv("ASSET_DIR", "static_files")
    monkeypatch.setenv("CACHE_TYPE", "redis")
    monkeypatch.setenv("REDIS_URL", "redis://localhost:6379/1")

    settings = reload_settings(monkeypatch)

    assert settings.api.api_key.get_secret_value() == "actual_api_key_from_env"
    assert settings.app.token_budget_usd == 1.50
    assert settings.app.site_dir == Path("/tmp/test_site")
    assert settings.app.template_dir == Path("custom_templates")
    assert settings.app.asset_dir == Path("static_files")
    assert settings.app.cache_type == "redis"
    assert settings.app.redis_url == "redis://localhost:6379/1"


def test_missing_required_env(monkeypatch):
    """Test that validation fails if a required environment variable is missing."""
    # Ensure PPLX_API_KEY is NOT set
    monkeypatch.delenv("PPLX_API_KEY", raising=False)

    with pytest.raises(ValidationError) as excinfo:
        reload_settings(monkeypatch)

    # Check that the error message mentions the missing field
    assert "api.api_key" in str(excinfo.value)
    assert "Field required" in str(excinfo.value)


def test_api_key_masking(monkeypatch):
    """Test that the API key is masked when accessed."""
    api_key = "super_secret_key_12345"
    monkeypatch.setenv("PPLX_API_KEY", api_key)
    settings = reload_settings(monkeypatch)

    # Check direct access and secret retrieval
    assert isinstance(settings.api.api_key, config.SecretStr)
    assert settings.api.api_key.get_secret_value() == api_key

    # Check representation (should be masked)
    assert repr(settings.api.api_key) == f"SecretStr('**********')"
    assert str(settings.api.api_key) == "**********"


def test_path_types(monkeypatch):
    """Test that path variables are loaded as Path objects."""
    monkeypatch.setenv("PPLX_API_KEY", "test_key_path")
    monkeypatch.setenv("SITE_DIR", "output/html")
    settings = reload_settings(monkeypatch)

    assert isinstance(settings.app.site_dir, Path)
    assert settings.app.site_dir == Path("output/html")
    assert isinstance(settings.app.template_dir, Path)
    assert settings.app.template_dir == Path("templates") # Default
    assert isinstance(settings.app.asset_dir, Path)
    assert settings.app.asset_dir == Path("assets") # Default

"""
Tests for configuration module.
Ensures environment validation works correctly for both local and production deployments.
"""

import pytest
from pydantic import ValidationError
from app.config import Settings, get_settings, validate_config


class TestSettingsValidation:
    """Test configuration validation."""

    def test_default_settings_local(self, monkeypatch):
        """Test that default settings work for local development."""
        # Clear any existing env vars
        for key in ["MONGODB_URL", "SECRET_KEY", "ENVIRONMENT"]:
            monkeypatch.delenv(key, raising=False)

        # Set minimal required env vars
        monkeypatch.setenv("MONGODB_URL", "mongodb://localhost:27017")

        settings = Settings()
        assert settings.environment == "local"
        assert settings.mongodb_url == "mongodb://localhost:27017"
        assert settings.database_name == "news_analytics"
        assert settings.secret_key == "dev-secret-key-change-in-production"

    def test_mongodb_url_validation_invalid_protocol(self, monkeypatch):
        """Test that invalid MongoDB URL protocol is rejected."""
        monkeypatch.setenv("MONGODB_URL", "http://localhost:27017")

        with pytest.raises(ValidationError) as exc_info:
            Settings()

        assert "must start with mongodb://" in str(exc_info.value)

    def test_mongodb_url_validation_empty(self, monkeypatch):
        """Test that empty MongoDB URL is rejected."""
        monkeypatch.setenv("MONGODB_URL", "")

        with pytest.raises(ValidationError) as exc_info:
            Settings()

        assert "must be set" in str(exc_info.value).lower()

    def test_mongodb_url_atlas_format(self, monkeypatch):
        """Test that MongoDB Atlas URL format is accepted."""
        atlas_url = "mongodb+srv://user:pass@cluster.mongodb.net/db?retryWrites=true"
        monkeypatch.setenv("MONGODB_URL", atlas_url)

        settings = Settings()
        assert settings.mongodb_url == atlas_url

    def test_secret_key_production_validation(self, monkeypatch):
        """Test that default secret key is rejected in production."""
        monkeypatch.setenv("ENVIRONMENT", "production")
        monkeypatch.setenv("MONGODB_URL", "mongodb://localhost:27017")
        monkeypatch.setenv("SECRET_KEY", "dev-secret-key-change-in-production")

        with pytest.raises(ValidationError) as exc_info:
            Settings()

        assert "must be changed in production" in str(exc_info.value)

    def test_secret_key_production_valid(self, monkeypatch):
        """Test that custom secret key is accepted in production."""
        monkeypatch.setenv("ENVIRONMENT", "production")
        monkeypatch.setenv("MONGODB_URL", "mongodb://localhost:27017")
        monkeypatch.setenv("SECRET_KEY", "my-super-secure-production-key-12345")

        settings = Settings()
        assert settings.secret_key == "my-super-secure-production-key-12345"

    def test_cors_origins_validation_invalid(self, monkeypatch):
        """Test that invalid CORS origins are rejected."""
        monkeypatch.setenv("MONGODB_URL", "mongodb://localhost:27017")
        monkeypatch.setenv("CORS_ORIGINS", "localhost:3000,invalid-url")

        with pytest.raises(ValidationError) as exc_info:
            Settings()

        assert "Invalid CORS origin" in str(exc_info.value)

    def test_cors_origins_validation_valid(self, monkeypatch):
        """Test that valid CORS origins are accepted."""
        monkeypatch.setenv("MONGODB_URL", "mongodb://localhost:27017")
        monkeypatch.setenv(
            "CORS_ORIGINS", "http://localhost:3000,https://app.vercel.app"
        )

        settings = Settings()
        origins = settings.get_cors_origins_list()
        assert len(origins) == 2
        assert "http://localhost:3000" in origins
        assert "https://app.vercel.app" in origins

    def test_cors_origins_empty_values_filtered(self, monkeypatch):
        """Test that empty CORS origins are filtered out."""
        monkeypatch.setenv("MONGODB_URL", "mongodb://localhost:27017")
        monkeypatch.setenv(
            "CORS_ORIGINS", "http://localhost:3000,  ,https://app.vercel.app,"
        )

        settings = Settings()
        origins = settings.get_cors_origins_list()
        assert len(origins) == 2
        assert "" not in origins

    def test_optional_openai_key(self, monkeypatch):
        """Test that OpenAI key is optional."""
        monkeypatch.setenv("MONGODB_URL", "mongodb://localhost:27017")
        monkeypatch.delenv("OPENAI_API_KEY", raising=False)

        settings = Settings()
        assert settings.openai_api_key is None

    def test_openai_key_provided(self, monkeypatch):
        """Test that OpenAI key is used when provided."""
        monkeypatch.setenv("MONGODB_URL", "mongodb://localhost:27017")
        monkeypatch.setenv("OPENAI_API_KEY", "sk-test-key-123")

        settings = Settings()
        assert settings.openai_api_key == "sk-test-key-123"

    def test_environment_types(self, monkeypatch):
        """Test that all environment types are accepted."""
        monkeypatch.setenv("MONGODB_URL", "mongodb://localhost:27017")

        for env in ["local", "development", "staging", "production"]:
            monkeypatch.setenv("ENVIRONMENT", env)
            if env == "production":
                monkeypatch.setenv("SECRET_KEY", "secure-key-for-prod")

            settings = Settings()
            assert settings.environment == env

    def test_rate_limit_configuration(self, monkeypatch):
        """Test rate limit configuration."""
        monkeypatch.setenv("MONGODB_URL", "mongodb://localhost:27017")
        monkeypatch.setenv("RATE_LIMIT_ENABLED", "false")
        monkeypatch.setenv("RATE_LIMIT_PER_MINUTE", "120")

        settings = Settings()
        assert settings.rate_limit_enabled is False
        assert settings.rate_limit_per_minute == 120

    def test_log_level_validation(self, monkeypatch):
        """Test log level validation."""
        monkeypatch.setenv("MONGODB_URL", "mongodb://localhost:27017")

        for level in ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]:
            monkeypatch.setenv("LOG_LEVEL", level)
            settings = Settings()
            assert settings.log_level == level

    def test_case_insensitive_env_vars(self, monkeypatch):
        """Test that environment variables are case-insensitive."""
        monkeypatch.setenv("mongodb_url", "mongodb://localhost:27017")
        monkeypatch.setenv("database_name", "test_db")

        settings = Settings()
        assert settings.mongodb_url == "mongodb://localhost:27017"
        assert settings.database_name == "test_db"


class TestConfigurationHelpers:
    """Test configuration helper functions."""

    def test_get_settings_singleton(self, monkeypatch):
        """Test that get_settings returns a singleton."""
        monkeypatch.setenv("MONGODB_URL", "mongodb://localhost:27017")

        # Clear the singleton
        import app.config

        app.config._settings = None

        settings1 = get_settings()
        settings2 = get_settings()

        assert settings1 is settings2

    def test_validate_config_success(self, monkeypatch, capsys):
        """Test that validate_config prints success message."""
        monkeypatch.setenv("MONGODB_URL", "mongodb://localhost:27017")

        # Clear the singleton
        import app.config

        app.config._settings = None

        validate_config()

        captured = capsys.readouterr()
        assert "Configuration validated successfully" in captured.out

    def test_validate_config_failure(self, monkeypatch):
        """Test that validate_config raises on invalid config."""
        monkeypatch.setenv("MONGODB_URL", "invalid-url")

        # Clear the singleton
        import app.config

        app.config._settings = None

        with pytest.raises(ValidationError):
            validate_config()


class TestProductionConfiguration:
    """Test production-specific configuration requirements."""

    def test_production_checklist(self, monkeypatch):
        """Test that production configuration meets all requirements."""
        # Set production environment
        monkeypatch.setenv("ENVIRONMENT", "production")
        monkeypatch.setenv(
            "MONGODB_URL", "mongodb+srv://user:pass@cluster.mongodb.net/prod"
        )
        monkeypatch.setenv(
            "SECRET_KEY", "very-secure-production-secret-key-generated-with-openssl"
        )
        monkeypatch.setenv("API_BASE_URL", "https://api.example.com")
        monkeypatch.setenv("FRONTEND_URL", "https://app.example.com")
        monkeypatch.setenv(
            "CORS_ORIGINS", "https://app.example.com,https://www.example.com"
        )

        settings = Settings()

        # Verify production requirements
        assert settings.environment == "production"
        assert settings.mongodb_url.startswith("mongodb+srv://")
        assert settings.secret_key != "dev-secret-key-change-in-production"
        assert settings.api_base_url.startswith("https://")
        assert settings.frontend_url.startswith("https://")
        assert all(
            origin.startswith("https://") for origin in settings.get_cors_origins_list()
        )

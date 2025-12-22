"""
Configuration module for News Analytics Platform.
Provides typed configuration with validation for both local and Vercel deployments.
"""
import os
from typing import Optional, Literal
from pydantic import Field, field_validator, ValidationInfo
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

# Load environment variables from .env file if present
load_dotenv()


class Settings(BaseSettings):
    """Application settings with validation."""
    
    # Environment
    environment: Literal["local", "development", "staging", "production"] = Field(
        default="local",
        description="Deployment environment"
    )
    
    # Database
    mongodb_url: str = Field(
        default="mongodb://localhost:27017",
        description="MongoDB connection URL. Use mongodb://mongodb:27017 for Docker or Atlas URL for production"
    )
    database_name: str = Field(
        default="news_analytics",
        description="MongoDB database name"
    )
    
    # API Configuration
    api_base_url: str = Field(
        default="http://localhost:8000",
        description="Backend API base URL for CORS and webhooks"
    )
    frontend_url: str = Field(
        default="http://localhost:3000",
        description="Frontend URL for CORS configuration"
    )
    
    # OpenAI (Optional)
    openai_api_key: Optional[str] = Field(
        default=None,
        description="OpenAI API key for AI fact-checking (optional)"
    )
    
    # Security
    secret_key: str = Field(
        default="dev-secret-key-change-in-production",
        description="Secret key for JWT token signing"
    )
    algorithm: str = Field(
        default="HS256",
        description="JWT algorithm"
    )
    access_token_expire_minutes: int = Field(
        default=30,
        description="JWT token expiration in minutes"
    )
    
    # Rate Limiting
    rate_limit_enabled: bool = Field(
        default=True,
        description="Enable rate limiting"
    )
    rate_limit_per_minute: int = Field(
        default=60,
        description="Rate limit requests per minute"
    )
    
    # CORS Configuration
    cors_origins: str = Field(
        default="http://localhost:3000,http://localhost:5173",
        description="Comma-separated list of allowed CORS origins"
    )
    
    # Logging
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = Field(
        default="INFO",
        description="Application log level"
    )
    
    @field_validator("mongodb_url")
    @classmethod
    def validate_mongodb_url(cls, v: str) -> str:
        """Validate MongoDB URL format."""
        if not v:
            raise ValueError("MONGODB_URL must be set")
        if not v.startswith(("mongodb://", "mongodb+srv://")):
            raise ValueError("MONGODB_URL must start with mongodb:// or mongodb+srv://")
        return v
    
    @field_validator("secret_key")
    @classmethod
    def validate_secret_key_production(cls, v: str, info: ValidationInfo) -> str:
        """Ensure secret key is changed in production."""
        environment = info.data.get("environment", "local")
        if environment == "production" and v == "dev-secret-key-change-in-production":
            raise ValueError(
                "SECRET_KEY must be changed in production! "
                "Generate a secure key with: openssl rand -hex 32"
            )
        return v
    
    @field_validator("cors_origins")
    @classmethod
    def validate_cors_origins(cls, v: str) -> str:
        """Validate CORS origins format."""
        origins = [origin.strip() for origin in v.split(",")]
        for origin in origins:
            if origin and not origin.startswith(("http://", "https://")):
                raise ValueError(f"Invalid CORS origin: {origin}. Must start with http:// or https://")
        return v
    
    def get_cors_origins_list(self) -> list[str]:
        """Get CORS origins as a list."""
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]
    
    class Config:
        env_file = ".env"
        case_sensitive = False
        extra = "ignore"


# Singleton instance
_settings: Optional[Settings] = None


def get_settings() -> Settings:
    """
    Get application settings singleton.
    Creates and validates settings on first call.
    """
    global _settings
    if _settings is None:
        try:
            _settings = Settings()
        except Exception as e:
            print("\n" + "=" * 80)
            print("❌ CONFIGURATION ERROR")
            print("=" * 80)
            print(f"\nFailed to load configuration: {str(e)}\n")
            print("Please check your environment variables and .env file.")
            print("\nRequired variables:")
            print("  - MONGODB_URL: MongoDB connection URL")
            print("  - SECRET_KEY: Secret key for JWT (required in production)")
            print("\nOptional variables:")
            print("  - OPENAI_API_KEY: OpenAI API key for AI features")
            print("  - ENVIRONMENT: local|development|staging|production")
            print("  - FRONTEND_URL: Frontend URL for CORS")
            print("\nSee .env.example for complete list.")
            print("=" * 80 + "\n")
            raise
    return _settings


def validate_config() -> None:
    """
    Validate configuration on application startup.
    Raises ValueError with helpful messages if configuration is invalid.
    """
    try:
        settings = get_settings()
        print("\n" + "=" * 80)
        print("✓ Configuration validated successfully")
        print("=" * 80)
        print(f"Environment: {settings.environment}")
        print(f"MongoDB: {settings.mongodb_url.split('@')[-1] if '@' in settings.mongodb_url else settings.mongodb_url}")
        print(f"Database: {settings.database_name}")
        print(f"API URL: {settings.api_base_url}")
        print(f"Frontend URL: {settings.frontend_url}")
        print(f"OpenAI: {'Enabled' if settings.openai_api_key else 'Disabled (using fallback)'}")
        print(f"Rate Limiting: {'Enabled' if settings.rate_limit_enabled else 'Disabled'}")
        print(f"Log Level: {settings.log_level}")
        print("=" * 80 + "\n")
    except Exception:
        raise


# Convenience exports
settings = get_settings()

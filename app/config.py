"""
Configuration settings for FixIt Tech Solutions.
This file will hold database connection strings, environment variables,
and other configuration parameters as the project grows.
"""

from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables or defaults.
    """
    # Application settings
    APP_NAME: str = "FixIt Tech Solutions"
    APP_VERSION: str = "0.1.0"
    DEBUG: bool = True
    
    # Database settings (to be configured in Phase 2)
    DATABASE_URL: Optional[str] = None
    
    # API settings
    API_PREFIX: str = "/api/v1"
    
    # Security settings (for future use)
    SECRET_KEY: Optional[str] = None
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Email settings (to be configured in Phase 6)
    SMTP_HOST: Optional[str] = None
    SMTP_PORT: Optional[int] = None
    SMTP_USER: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    
    # Pagination defaults
    DEFAULT_PAGE_SIZE: int = 20
    MAX_PAGE_SIZE: int = 100
    
    class Config:
        env_file = ".env"
        case_sensitive = True


# Global settings instance
settings = Settings()

"""Application configuration using Pydantic settings."""
from typing import Optional
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict
import os


class Settings(BaseSettings):
    """Application settings."""
    
    model_config = SettingsConfigDict(
        env_file=[".env", "../.env"],
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"
    )
    
    # Strava Configuration
    STRAVA_CLIENT_ID: str = Field(..., description="Strava API client ID")
    STRAVA_CLIENT_SECRET: str = Field(..., description="Strava API client secret")
    STRAVA_REFRESH_TOKEN: str = Field(..., description="Strava refresh token")
    STRAVA_ACCESS_TOKEN: str = Field(default="", description="Strava access token")
    STRAVA_WEBHOOK_VERIFY_TOKEN: str = Field(..., description="Strava webhook verification token")
    
    # Supabase Configuration
    SUPABASE_URL: str = Field(..., description="Supabase project URL")
    SUPABASE_KEY: str = Field(..., description="Supabase anonymous key")
    SUPABASE_SERVICE_KEY: str = Field(..., description="Supabase service role key")
    
    # Database Configuration (OPTIONAL - for direct PostgreSQL if DNS works)
    DATABASE_URL: str = Field(default="", description="Database connection URL (optional)")
    DATABASE_POOL_SIZE: int = Field(default=10, description="Database connection pool size")
    DATABASE_MAX_OVERFLOW: int = Field(default=20, description="Database max overflow connections")
    
    # Application Configuration
    APP_NAME: str = Field(default="Strava Report", description="Application name")
    APP_VERSION: str = Field(default="0.1.0", description="Application version")
    DEBUG: bool = Field(default=False, description="Debug mode")
    LOG_LEVEL: str = Field(default="INFO", description="Logging level")
    
    # API Configuration
    API_HOST: str = Field(default="0.0.0.0", description="API host")
    API_PORT: int = Field(default=8000, description="API port")
    API_RELOAD: bool = Field(default=False, description="API auto-reload")
    
    # Webhook Configuration
    WEBHOOK_SECRET: str = Field(default="", description="Webhook secret for signature verification")
    WEBHOOK_TIMEOUT: int = Field(default=30, description="Webhook timeout in seconds")
    
    # ETL Configuration
    ETL_BATCH_SIZE: int = Field(default=100, description="ETL batch size")
    ETL_RETRY_ATTEMPTS: int = Field(default=3, description="ETL retry attempts")
    ETL_RETRY_DELAY: int = Field(default=5, description="ETL retry delay in seconds")
    
    # Frontend Configuration
    STREAMLIT_SERVER_PORT: int = Field(default=8501, description="Streamlit server port")
    STREAMLIT_SERVER_ADDRESS: str = Field(default="0.0.0.0", description="Streamlit server address")

    def use_supabase_client(self) -> bool:
        """Check if we should use Supabase client instead of direct PostgreSQL."""
        # Use Supabase client if DATABASE_URL is not configured or if we prefer HTTP API
        return not self.DATABASE_URL or self.DATABASE_URL == ""


settings = Settings()

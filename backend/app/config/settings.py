import os
from typing import Optional
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    # Database Settings
    database_url: str = Field(
        default="sqlite:///leetsync.db",
        validation_alias="DATABASE_URL",
        description="SQLAlchemy database connection URL"
    )
    
    # GitHub Integration Settings
    github_token: str = Field(
        default="",
        validation_alias="GITHUB_TOKEN",
        description="GitHub Personal Access Token"
    )
    github_repo: str = Field(
        default="",
        validation_alias="GITHUB_REPO",
        description="GitHub target repository in 'owner/repo' format"
    )
    
    # LeetCode Integration Settings
    leetcode_session: str = Field(
        default="",
        validation_alias="LEETCODE_SESSION",
        description="LeetCode cookie session string (LEETCODE_SESSION)"
    )
    leetcode_csrf_token: str = Field(
        default="",
        validation_alias="LEETCODE_CSRF_TOKEN",
        description="LeetCode CSRF Token"
    )
    
    # Engine Settings
    sync_interval_minutes: int = Field(
        default=5,
        validation_alias="SYNC_INTERVAL_MINUTES",
        description="Synchronization interval in minutes"
    )
    log_level: str = Field(
        default="INFO",
        validation_alias="LOG_LEVEL",
        description="Logging level"
    )

    # Configuration to load from .env file
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        populate_by_name=True
    )

    @field_validator("github_repo")
    @classmethod
    def validate_github_repo(cls, v: str) -> str:
        if v and "/" not in v:
            raise ValueError("github_repo must be in the format 'owner/repo'")
        return v

    def is_auth_configured(self) -> bool:
        """Checks if both GitHub and LeetCode credentials are set."""
        return bool(self.github_token and self.github_repo and self.leetcode_session)

# Global settings instance
settings = Settings()

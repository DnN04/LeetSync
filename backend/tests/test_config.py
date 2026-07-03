import os
import pytest
from app.config.settings import Settings

def test_default_settings():
    settings = Settings(_env_file=None)  # Ignore any existing .env for this test
    assert settings.database_url == "sqlite:///leetsync.db"
    assert settings.github_token == ""
    assert settings.github_repo == ""
    assert settings.leetcode_session == ""
    assert settings.leetcode_csrf_token == ""
    assert settings.sync_interval_minutes == 5
    assert settings.log_level == "INFO"

def test_validation_github_repo():
    with pytest.raises(ValueError, match="github_repo must be in the format 'owner/repo'"):
        Settings(github_repo="invalid_repo_format", _env_file=None)

def test_auth_configured():
    # Unconfigured defaults
    settings = Settings(_env_file=None)
    assert not settings.is_auth_configured()
    
    # Configured
    configured_settings = Settings(
        github_token="ghp_testtoken",
        github_repo="owner/repo",
        leetcode_session="cookie_session_val",
        _env_file=None
    )
    assert configured_settings.is_auth_configured()

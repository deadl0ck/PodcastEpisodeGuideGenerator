"""Environment variable loading, validation, and safe logging helpers."""

from __future__ import annotations

import os
import sys
import logging
from dotenv import load_dotenv

ENV_VARS: dict[str, str | None] = {}
YOUTUBE_API_KEY = "YOUTUBE_API_KEY"
GOOGLE_API_KEY = "GOOGLE_API_KEY"  # Legacy alias retained for backward compatibility.
YOUTUBE_PLAYLIST_ID = "YOUTUBE_PLAYLIST_ID"
PODBEAN_RSS_FEED = 'PODBEAN_RSS_FEED'
REDDIT_CLIENT_ID = "REDDIT_CLIENT_ID"
REDDIT_CLIENT_SECRET = "REDDIT_CLIENT_SECRET"
REDDIT_USERNAME = "REDDIT_USERNAME"
REDDIT_PASSWORD = "REDDIT_PASSWORD"
REDDIT_USER_AGENT = "REDDIT_USER_AGENT"
LOG_LEVEL = "LOG_LEVEL"
TENP_GEMINI_API_KEY = "TENP_GEMINI_API_KEY"
# All names listed here are checked for presence at startup
ENV_VAR_NAMES = [YOUTUBE_API_KEY,
                 YOUTUBE_PLAYLIST_ID,
                 PODBEAN_RSS_FEED,
                 REDDIT_CLIENT_ID,
                 REDDIT_CLIENT_SECRET,
                 REDDIT_USERNAME,
                 REDDIT_PASSWORD,
                 REDDIT_USER_AGENT]

# Optional env vars are loaded and logged but not required for startup.
OPTIONAL_ENV_VAR_NAMES = [LOG_LEVEL, TENP_GEMINI_API_KEY]

logger = logging.getLogger(__name__)


class EnvVarUtils:
    """Load, validate, and safely log required runtime environment variables."""

    SENSITIVE_ENV_VAR_TOKENS = ["PASSWORD", "SECRET", "API_KEY", "TOKEN"]

    @staticmethod
    def init() -> None:
        """Load variables from .env, validate required values, and log them safely."""
        load_dotenv()
        EnvVarUtils.populate_env_vars()
        EnvVarUtils.check_env_vars()
        for s in EnvVarUtils.get_env_vars_as_string_list():
            logger.info(s)

    @staticmethod
    def get_log_level() -> int:
        """Return the configured logging level, defaulting to INFO."""
        value = EnvVarUtils.get_env_var(LOG_LEVEL)
        if value is None:
            return logging.INFO

        mapped_level = logging.getLevelName(value.upper())
        if isinstance(mapped_level, int):
            return mapped_level

        logger.warning('Invalid LOG_LEVEL "%s" - defaulting to INFO', value)
        return logging.INFO

    @staticmethod
    def is_sensitive_env_var(name: str) -> bool:
        """Return whether the env var name should be masked in logs."""
        upper_name = name.upper()
        return any(token in upper_name for token in EnvVarUtils.SENSITIVE_ENV_VAR_TOKENS)

    @staticmethod
    def mask_env_var_value(name: str, value: str | None) -> str:
        """Mask sensitive env var values while keeping short suffixes visible."""
        if value is None:
            return "None"
        if not EnvVarUtils.is_sensitive_env_var(name):
            return value

        if len(value) <= 4:
            return "*" * len(value)
        return f"{'*' * (len(value) - 4)}{value[-4:]}"

    @staticmethod
    def get_env_var(name: str) -> str | None:
        """Return the current value for an environment variable from cache or process env."""
        if name not in ENV_VARS:
            ENV_VARS[name] = os.getenv(name)
        return ENV_VARS[name]

    @staticmethod
    def populate_env_vars() -> None:
        """Refresh the in-memory cache from the current process environment."""
        # Primary key name for TWIR YouTube API.
        ENV_VARS[YOUTUBE_API_KEY] = os.getenv(YOUTUBE_API_KEY) or os.getenv(GOOGLE_API_KEY)
        for current in ENV_VAR_NAMES + OPTIONAL_ENV_VAR_NAMES:
            if current == YOUTUBE_API_KEY:
                continue
            ENV_VARS[current] = os.getenv(current)

    @staticmethod
    def is_valid_env_var(value: str | None, env_var_name: str) -> bool:
        """Return whether a required environment variable has a usable value."""
        if value is None:
            logger.error('You must specify the environment variable "%s"', env_var_name)
            return False
        return True

    @staticmethod
    def check_env_vars() -> None:
        """Exit the process when required environment variables are missing."""
        errors_found = False

        for current in ENV_VAR_NAMES:
            if not EnvVarUtils.is_valid_env_var(ENV_VARS[current], current):
                errors_found = True

        if errors_found:
            sys.exit(1)

    @staticmethod
    def get_env_vars_as_string_list() -> list[str]:
        """Return formatted environment variable log lines with masking applied."""
        return_list: list[str] = []
        for key in ENV_VARS:
            safe_value = EnvVarUtils.mask_env_var_value(key, ENV_VARS[key])
            return_list.append(f'Environment Variable "{key}": "{safe_value}"')
        return return_list


load_dotenv()

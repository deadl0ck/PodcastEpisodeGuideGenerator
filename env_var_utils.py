# env_var_utils.py
# Loads environment variables from .env (via python-dotenv) and validates
# that all required values are present before the application starts.
import os
import sys
import logging
from dotenv import load_dotenv

ENV_VARS = {}  # In-memory store populated by EnvVarUtils.init()
GOOGLE_API_KEY = "GOOGLE_API_KEY"
YOUTUBE_PLAYLIST_ID = "YOUTUBE_PLAYLIST_ID"
PODBEAN_RSS_FEED = 'PODBEAN_RSS_FEED'
REDDIT_CLIENT_ID = "REDDIT_CLIENT_ID"
REDDIT_CLIENT_SECRET = "REDDIT_CLIENT_SECRET"
REDDIT_USERNAME = "REDDIT_USERNAME"
REDDIT_PASSWORD = "REDDIT_PASSWORD"
REDDIT_USER_AGENT = "REDDIT_USER_AGENT"
LOG_LEVEL = "LOG_LEVEL"
# All names listed here are checked for presence at startup
ENV_VAR_NAMES = [GOOGLE_API_KEY,
                 YOUTUBE_PLAYLIST_ID,
                 PODBEAN_RSS_FEED,
                 REDDIT_CLIENT_ID,
                 REDDIT_CLIENT_SECRET,
                 REDDIT_USERNAME,
                 REDDIT_PASSWORD,
                 REDDIT_USER_AGENT]

# Optional env vars are loaded and logged but not required for startup.
OPTIONAL_ENV_VAR_NAMES = [LOG_LEVEL]

logger = logging.getLogger(__name__)


class EnvVarUtils:
    SENSITIVE_ENV_VAR_TOKENS = ["PASSWORD", "SECRET", "API_KEY", "TOKEN"]

    @staticmethod
    def init() -> None:
        EnvVarUtils.populate_env_vars()
        EnvVarUtils.check_env_vars()
        for s in EnvVarUtils.get_env_vars_as_string_list():
            logger.info(s)

    @staticmethod
    def get_log_level() -> int:
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
        upper_name = name.upper()
        return any(token in upper_name for token in EnvVarUtils.SENSITIVE_ENV_VAR_TOKENS)

    @staticmethod
    def mask_env_var_value(name: str, value: str | None) -> str:
        if value is None:
            return "None"
        if not EnvVarUtils.is_sensitive_env_var(name):
            return value

        if len(value) <= 4:
            return "*" * len(value)
        return f"{'*' * (len(value) - 4)}{value[-4:]}"

    @staticmethod
    def get_env_var(name: str) -> str:
        return ENV_VARS[name]

    @staticmethod
    def populate_env_vars() -> None:
        for current in ENV_VAR_NAMES + OPTIONAL_ENV_VAR_NAMES:
            ENV_VARS[current] = os.getenv(current)

    @staticmethod
    def is_valid_env_var(value: str, env_var_name: str) -> bool:
        if value is None:
            logger.error('You must specify the environment variable "%s"', env_var_name)
            return False
        return True

    @staticmethod
    def check_env_vars() -> None:
        errors_found = False

        for current in ENV_VAR_NAMES:
            if not EnvVarUtils.is_valid_env_var(ENV_VARS[current], current):
                errors_found = True

        if errors_found:
            sys.exit(1)

    @staticmethod
    def get_env_vars_as_string_list() -> list[str]:
        return_list = []
        for key in ENV_VARS.keys():
            safe_value = EnvVarUtils.mask_env_var_value(key, ENV_VARS[key])
            return_list.append(f'Environment Variable "{key}": "{safe_value}"')
        return return_list


load_dotenv()
EnvVarUtils.populate_env_vars()

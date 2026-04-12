from __future__ import annotations

import logging
import os

from env_var_utils import EnvVarUtils


class _ColorFormatter(logging.Formatter):
    """ANSI-colored formatter for terminal log readability."""

    _RESET = "\033[0m"
    _LEVEL_COLOURS = {
        logging.INFO: "\033[32m",      # green
        logging.WARNING: "\033[38;5;214m",  # orange-ish
        logging.ERROR: "\033[31m",     # red
        logging.CRITICAL: "\033[31m",  # red
    }

    def format(self, record: logging.LogRecord) -> str:
        prefix = f"{self.formatTime(record, self.datefmt)} {record.levelname} [{record.name}]"
        message = record.getMessage()

        colour = self._LEVEL_COLOURS.get(record.levelno)
        if colour:
            message = f"{colour}{message}{self._RESET}"

        formatted = f"{prefix} {message}"

        if record.exc_info:
            formatted = f"{formatted}\n{self.formatException(record.exc_info)}"
        if record.stack_info:
            formatted = f"{formatted}\n{self.formatStack(record.stack_info)}"
        return formatted


def configure_logging() -> None:
    """Shared logging setup for podcast entrypoints."""
    root_logger = logging.getLogger()
    root_logger.handlers.clear()
    root_logger.setLevel(EnvVarUtils.get_log_level())

    handler = logging.StreamHandler()
    handler.setFormatter(_ColorFormatter('%(asctime)s %(levelname)s [%(name)s] %(message)s'))
    root_logger.addHandler(handler)

    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("requests").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("google_genai").setLevel(logging.WARNING)


def get_test_run_settings() -> tuple[bool, int]:
    """Read GUIDE_TEST_* settings from environment in one place."""
    test_run = os.getenv("GUIDE_TEST_RUN", "false").lower() in {"1", "true", "yes"}
    test_run_count = int(os.getenv("GUIDE_TEST_COUNT", "5"))
    return test_run, test_run_count

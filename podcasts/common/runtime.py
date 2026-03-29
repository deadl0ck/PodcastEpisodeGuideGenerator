from __future__ import annotations

import logging
import os

from env_var_utils import EnvVarUtils


def configure_logging() -> None:
    """Shared logging setup for podcast entrypoints."""
    logging.basicConfig(
        level=EnvVarUtils.get_log_level(),
        format='%(asctime)s %(levelname)s [%(name)s] %(message)s'
    )
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("requests").setLevel(logging.WARNING)


def get_test_run_settings() -> tuple[bool, int]:
    """Read GUIDE_TEST_* settings from environment in one place."""
    test_run = os.getenv("GUIDE_TEST_RUN", "false").lower() in {"1", "true", "yes"}
    test_run_count = int(os.getenv("GUIDE_TEST_COUNT", "5"))
    return test_run, test_run_count

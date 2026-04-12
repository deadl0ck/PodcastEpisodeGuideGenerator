"""Run one or more podcast guide generators from a single command.

This runner intentionally generates separate PDFs per podcast.
"""
from __future__ import annotations

import argparse
import os
import subprocess
import sys
from pathlib import Path

from cache_paths import RA_PROVIDER_KEY, TENP_PROVIDER_KEY, TWIR_PROVIDER_KEY, ZTTP_PROVIDER_KEY
from constants import get_provider_constants


WORKSPACE_ROOT = Path(__file__).resolve().parent
CLI_ALL = "all"
PODCAST_TWIR = TWIR_PROVIDER_KEY.lower()
PODCAST_ZTTP = ZTTP_PROVIDER_KEY.lower()
PODCAST_RA = RA_PROVIDER_KEY.lower()
PODCAST_TENP = TENP_PROVIDER_KEY.lower()
SUPPORTED_PODCASTS = (PODCAST_TWIR, PODCAST_ZTTP, PODCAST_RA, PODCAST_TENP)


def _build_command(podcast_key: str) -> list[str]:
    """Return the subprocess command for the selected provider entrypoint."""
    if podcast_key == PODCAST_TWIR:
        return [sys.executable, str(WORKSPACE_ROOT / "podcasts" / PODCAST_TWIR / "main.py")]
    if podcast_key == PODCAST_ZTTP:
        return [sys.executable, str(WORKSPACE_ROOT / "podcasts" / PODCAST_ZTTP / "main.py")]
    if podcast_key == PODCAST_RA:
        return [sys.executable, str(WORKSPACE_ROOT / "podcasts" / PODCAST_RA / "main.py")]
    if podcast_key == PODCAST_TENP:
        return [sys.executable, str(WORKSPACE_ROOT / "podcasts" / "tenp" / "main.py")]
    raise ValueError(f"Unsupported podcast key: {podcast_key}")


def _parse_podcast_selection(raw_value: str) -> list[str]:
    """Parse and normalize the requested podcast list from CLI input."""
    requested = [item.strip().lower() for item in raw_value.split(",") if item.strip()]
    if not requested:
        raise ValueError("At least one podcast must be selected")

    selected: list[str] = []
    for key in requested:
        if key == CLI_ALL:
            for supported in SUPPORTED_PODCASTS:
                if supported not in selected:
                    selected.append(supported)
            continue

        if key not in SUPPORTED_PODCASTS:
            allowed = ", ".join((*SUPPORTED_PODCASTS, CLI_ALL))
            raise ValueError(f"Unknown podcast '{key}'. Allowed values: {allowed}")

        if key not in selected:
            selected.append(key)

    return selected


def main() -> int:
    """Parse CLI arguments, run the selected providers, and return a process exit code."""
    parser = argparse.ArgumentParser(
        description="Generate separate podcast episode guides for selected podcasts."
    )
    parser.add_argument(
        "--podcasts",
        default=PODCAST_TWIR,
        help=(
            f"Comma-separated list: {','.join(SUPPORTED_PODCASTS)} "
            f"or {CLI_ALL} (default: {PODCAST_TWIR})"
        ),
    )
    parser.add_argument(
        "--continue-on-error",
        action="store_true",
        help="Continue with remaining podcasts if one fails.",
    )
    parser.add_argument(
        "--test",
        action="store_true",
        help="Run providers in test mode (subset of episodes).",
    )
    parser.add_argument(
        "--test-count",
        type=int,
        default=5,
        help="Number of episodes to process when --test is enabled.",
    )
    args = parser.parse_args()

    try:
        selected = _parse_podcast_selection(args.podcasts)
    except ValueError as exc:
        print(f"Selection error: {exc}")
        return 2

    print(f"Selected podcasts: {', '.join(selected)}")
    for podcast_key in selected:
        provider_constants = get_provider_constants(podcast_key)
        output_pdf = Path(provider_constants.output.pdf_location) / provider_constants.output.pdf_name
        print(f"- {provider_constants.provider_key} output: {output_pdf}")

    failures: list[str] = []

    for podcast_key in selected:
        cmd = _build_command(podcast_key)
        print(f"\n=== Generating {podcast_key.upper()} guide ===")
        env = os.environ.copy()
        pythonpath = env.get("PYTHONPATH", "")
        env["PYTHONPATH"] = (
            f"{WORKSPACE_ROOT}{os.pathsep}{pythonpath}" if pythonpath else str(WORKSPACE_ROOT)
        )
        if args.test:
            env["GUIDE_TEST_RUN"] = "true"
            env["GUIDE_TEST_COUNT"] = str(args.test_count)

        result = subprocess.run(cmd, cwd=str(WORKSPACE_ROOT), check=False, env=env)
        if result.returncode != 0:
            failures.append(podcast_key)
            print(f"FAILED: {podcast_key.upper()} returned exit code {result.returncode}")
            if not args.continue_on_error:
                break
        else:
            print(f"COMPLETED: {podcast_key.upper()} guide generated")

    if failures:
        print(f"\nRun finished with failures: {', '.join(failures)}")
        return 1

    print("\nRun finished successfully for all selected podcasts")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
from __future__ import annotations

import logging

from env_var_utils import EnvVarUtils, TEN_P_GEMINI_API_KEY

logger = logging.getLogger(__name__)


class BasicAI:
    def __init__(self):
        self.model = "gemini-2.5-pro"
        self.default_question = (
            "Can you extract the title of next month's game from this text? "
            "If it is not mentioned, return 'No Game'."
        )
        self._client = None
        self._disabled_for_run = False

    @property
    def is_disabled_for_run(self) -> bool:
        return self._disabled_for_run

    def _get_client(self):
        if self._client is not None:
            return self._client

        api_key = EnvVarUtils.get_env_var(TEN_P_GEMINI_API_KEY)
        if not api_key:
            logger.warning("TEN_P Gemini API key is not configured; skipping AI extraction")
            return None

        try:
            import google.genai as genai
        except ImportError:
            logger.warning("google-genai package is not installed; skipping AI extraction")
            return None

        self._client = genai.Client(api_key=api_key)
        return self._client

    def get_next_months_game(self, text: str) -> str:
        if self._disabled_for_run:
            return "No Game"

        client = self._get_client()
        if client is None:
            return "No Game"

        question = f"{self.default_question}\n{text}"
        try:
            response = client.models.generate_content(model=self.model, contents=question)
            return (response.text or "No Game").strip()
        except Exception as exc:  # google-genai has a rich exception hierarchy; handle defensively.
            message = str(exc)
            logger.warning("TenP AI extraction failed; falling back to 'No Game': %s", message)
            if "API key not valid" in message or "API_KEY_INVALID" in message:
                logger.warning("TEN_P_GEMINI_API_KEY appears invalid; disabling AI extraction for this run")
                self._disabled_for_run = True
            return "No Game"

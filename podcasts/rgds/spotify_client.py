from __future__ import annotations

import base64
import http.server
import json
import logging
import os
import socketserver
import threading
import time
import urllib.parse
import webbrowser
from dataclasses import dataclass
from urllib.parse import urlparse

import requests

from podcasts.rgds.page_constants import AUTH_CACHE_LOCATION, OAUTH_SCOPE, redirect_port

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class SpotifyAuthConfig:
    client_id: str
    client_secret: str
    redirect_uri: str
    show_id: str
    refresh_token: str | None = None


class _ReusableTCPServer(socketserver.TCPServer):
    allow_reuse_address = True


class RGDSSpotifyClient:
    """Spotify API client for RGDS provider with refresh-token auth support."""

    def __init__(self, config: SpotifyAuthConfig):
        self.config = config
        self._access_token = self._build_access_token()

    def get_show_info(self) -> dict:
        return self._request_json(f"https://api.spotify.com/v1/shows/{self.config.show_id}")

    def get_episodes(self) -> list[dict]:
        episodes: list[dict] = []
        next_url = f"https://api.spotify.com/v1/shows/{self.config.show_id}/episodes/?limit=50&offset=0"
        max_retries = 3
        while next_url:
            retry_count = 0
            while retry_count < max_retries:
                try:
                    payload = self._request_json(next_url)
                    episodes.extend(payload.get("items", []))
                    next_url = payload.get("next")
                    break
                except requests.exceptions.Timeout as e:
                    retry_count += 1
                    if retry_count >= max_retries:
                        logger.warning(
                            "Spotify API request timeout after %d retries for %s",
                            max_retries,
                            next_url,
                        )
                        raise
                    logger.info("Spotify API timeout, retrying (attempt %d/%d)", retry_count, max_retries)
                except requests.exceptions.ConnectionError as e:
                    retry_count += 1
                    if retry_count >= max_retries:
                        logger.warning(
                            "Spotify API connection error after %d retries: %s",
                            max_retries,
                            str(e)[:100],
                        )
                        raise
                    logger.info("Spotify API connection error, retrying (attempt %d/%d)", retry_count, max_retries)
            else:
                break
        return episodes

    def _request_json(self, url: str) -> dict:
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self._access_token}",
            "Accept": "application/json",
        }
        response = requests.get(url, headers=headers, timeout=(10, 30))
        response.raise_for_status()
        return response.json()

    def _build_access_token(self) -> str:
        refresh_token = self._resolve_refresh_token()
        if refresh_token:
            logger.info("Using Spotify refresh token flow for RGDS")
            return self._refresh_access_token(refresh_token)

        logger.warning("No RGDS refresh token found; starting interactive Spotify auth bootstrap")
        code = self._get_auth_code()
        token_data = self._exchange_code_for_tokens(code)
        access_token = token_data["access_token"]
        self._save_refresh_token(token_data.get("refresh_token"))
        return access_token

    def _resolve_refresh_token(self) -> str | None:
        if self.config.refresh_token:
            return self.config.refresh_token

        if not os.path.exists(AUTH_CACHE_LOCATION):
            return None

        try:
            with open(AUTH_CACHE_LOCATION, "r", encoding="utf-8") as handle:
                cached = json.load(handle)
            token = cached.get("refresh_token")
            if token:
                logger.info("Loaded RGDS refresh token from auth cache")
            return token
        except (json.JSONDecodeError, OSError):
            logger.warning("Could not read RGDS auth cache, continuing without cached refresh token")
            return None

    def _refresh_access_token(self, refresh_token: str) -> str:
        token_headers = {
            "Authorization": f"Basic {self._encoded_credentials()}",
            "Content-Type": "application/x-www-form-urlencoded",
        }
        token_data = {
            "grant_type": "refresh_token",
            "refresh_token": refresh_token,
        }

        response = requests.post(
            "https://accounts.spotify.com/api/token",
            data=token_data,
            headers=token_headers,
            timeout=(10, 30),
        )
        response.raise_for_status()
        body = response.json()
        access_token = body.get("access_token")
        if not access_token:
            raise RuntimeError("Spotify refresh token exchange did not return access_token")

        returned_refresh = body.get("refresh_token")
        if returned_refresh:
            self._save_refresh_token(returned_refresh)
        return access_token

    def _exchange_code_for_tokens(self, code: str) -> dict:
        token_headers = {
            "Authorization": f"Basic {self._encoded_credentials()}",
            "Content-Type": "application/x-www-form-urlencoded",
        }
        token_data = {
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": self.config.redirect_uri,
        }

        response = requests.post(
            "https://accounts.spotify.com/api/token",
            data=token_data,
            headers=token_headers,
            timeout=(10, 30),
        )
        response.raise_for_status()
        body = response.json()
        if "access_token" not in body:
            raise RuntimeError("Spotify token exchange failed: no access token in response")
        return body

    def _encoded_credentials(self) -> str:
        credentials = f"{self.config.client_id}:{self.config.client_secret}".encode("utf-8")
        return base64.b64encode(credentials).decode("utf-8")

    def _get_auth_code(self) -> str:
        parsed = urlparse(self.config.redirect_uri)
        host = parsed.hostname or "127.0.0.1"
        port = redirect_port(self.config.redirect_uri)
        callback_path = parsed.path or "/callback"
        auth_code: list[str | None] = [None]

        class CallbackHandler(http.server.BaseHTTPRequestHandler):
            def do_GET(self):
                incoming = urllib.parse.urlparse(self.path)
                if incoming.path != callback_path:
                    self.send_response(404)
                    self.end_headers()
                    return
                query = urllib.parse.parse_qs(incoming.query)
                auth_code[0] = query.get("code", [None])[0]
                self.send_response(200)
                self.send_header("Content-type", "text/html")
                self.end_headers()
                self.wfile.write(b"Authorization complete. You can close this window.")

            def log_message(self, format, *args):
                return

        params = {
            "client_id": self.config.client_id,
            "response_type": "code",
            "redirect_uri": self.config.redirect_uri,
            "scope": OAUTH_SCOPE,
        }
        auth_url = "https://accounts.spotify.com/authorize?" + urllib.parse.urlencode(params)

        with _ReusableTCPServer((host, port), CallbackHandler) as httpd:
            server_thread = threading.Thread(target=httpd.serve_forever, daemon=True)
            server_thread.start()
            webbrowser.open(auth_url)

            for _ in range(180):
                if auth_code[0]:
                    httpd.shutdown()
                    server_thread.join(timeout=1)
                    return str(auth_code[0])
                time.sleep(1)

            httpd.shutdown()
            server_thread.join(timeout=1)

        raise RuntimeError("Timed out waiting for Spotify authorization callback")

    def _save_refresh_token(self, refresh_token: str | None) -> None:
        if not refresh_token:
            return

        os.makedirs(os.path.dirname(AUTH_CACHE_LOCATION), exist_ok=True)
        with open(AUTH_CACHE_LOCATION, "w", encoding="utf-8") as handle:
            json.dump({"refresh_token": refresh_token}, handle)
        logger.info("Saved RGDS refresh token to auth cache")

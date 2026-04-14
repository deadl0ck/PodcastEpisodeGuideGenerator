# Podcast Episode Guide Generator

Generates PDF "magazine-style" episode guides for:
- [This Week in Retro (TWIR)](https://www.youtube.com/@ThisWeekinRetro/videos)
- [Zapped to the Past (ZTTP)](https://zappedtothepast.com/)
- [Retro Asylum (RA)](https://retroasylum.com/)
- [Ten Pence Arcade (10P)](https://www.tenpencearcade.com/)
- [Retro Game Discussion Show (RGDS)](https://open.spotify.com/show/00sL9tgDezr0PRSzd3C7H6)

Each run produces:
- A cover page
- A clickable Table of Contents
- One A4 page per episode with links
- Podcast-specific feature pages (TWIR QoW list, ZTTP game list)
- TWIR also writes a companion CSV with episode metadata

## Table of Contents

- [Prerequisites](#prerequisites)
- [Quick Start (Beginner)](#quick-start-beginner)
- [Installation](#installation)
- [Configuration](#configuration)
- [Running](#running)
- [Utility Scripts](#utility-scripts)
- [Unified Multi-Podcast Run](#unified-multi-podcast-run)
- [Project Structure](#project-structure)
- [Logging](#logging)
- [Image Cache](#image-cache)
- [Ten Pence AI Extraction](#ten-pence-ai-extraction)
- [Developer Notes](#developer-notes)
- [Unit Tests](#unit-tests)
- [Dependencies](#dependencies)

---

## Prerequisites

- Python 3.9 or later (tested on 3.9 and 3.10)
- A **Google API key** with the YouTube Data API v3 enabled (TWIR only)
- Optional: a **Gemini API key** for Ten Pence next-month-game extraction
- A **Reddit account** with a registered script application (TWIR QoW only)
- Internet access to `retroasylum.com` for the RA guide (no API keys required)
- Spotify app credentials for RGDS (`RGDS_CLIENT_ID`, `RGDS_CLIENT_SECRET`, `RGDS_REDIRECT_URI`)

---

## Quick Start (Beginner)

If you want the shortest path from zero to running, follow exactly one of these flows.

### macOS / Linux

```bash
# 1) Open a terminal and go to the project folder
cd /path/to/PodcastEpisoideGuideGenerator

# 2) Create and activate a virtual environment
python3 -m venv .venv
source .venv/bin/activate

# 3) Install dependencies
pip install -r requirements.txt

# 4) Create .env from the example in this README

# 5) Run the app
python run_guides.py --podcasts [twir | zttp | ra | 10p | rgds | all]
```

### Windows (PowerShell)

```powershell
# 1) Open PowerShell and go to the project folder
cd C:\path\to\PodcastEpisoideGuideGenerator

# 2) Create and activate a virtual environment
py -3 -m venv .venv
.\.venv\Scripts\Activate.ps1

# 3) Install dependencies
pip install -r requirements.txt

# 4) Create .env from the example in this README

# 5) Run the app
python run_guides.py --podcasts [twir | zttp | ra | 10p | rgds | all]
```

Output files are written to your Desktop (podcast dependent):
- `TWiR Episode Guide.pdf`
- `TWiR_Data.csv`
- `ZTTP Episode Guide.pdf`
- `RA Episode Guide.pdf`
- `Ten Pence Arcade Episode Guide.pdf`
- `RGDS Episode Guide.pdf`

---

## Installation

Verify your Python version first:

```bash
python3 --version      # macOS/Linux
py -3 --version        # Windows
```

`venv` uses whichever Python interpreter you run it with.

- `python3 -m venv .venv` creates a venv from your default `python3`.
- `python3.10 -m venv .venv310` creates a Python 3.10 venv specifically.

Recommended default setup (works with your installed Python 3.x).

### macOS / Linux

```bash
python3 -m venv .venv
source .venv/bin/activate
python --version
pip install -r requirements.txt
```

### Windows (PowerShell)

```powershell
py -3 -m venv .venv
.\.venv\Scripts\Activate.ps1
python --version
pip install -r requirements.txt
```

Optional: if you specifically want to pin to Python 3.10 (known-good version):

### macOS / Linux (Python 3.10 pinned)

```bash
python3.10 -m venv .venv310
source .venv310/bin/activate
python --version                      # Should show Python 3.10.x
pip install -r requirements.txt
```

### Windows (PowerShell, Python 3.10 pinned)

```powershell
py -3.10 -m venv .venv310
.\.venv310\Scripts\Activate.ps1
python --version
pip install -r requirements.txt
```

If `python3.10` is not available, you can still create a venv with your installed Python 3.x version.

> **Note:** The YouTube client library is imported as `from pyyoutube import Api` but the pip package name is `python-youtube`.

---

## Configuration

### 1. `.env` file

Create a `.env` file in the project root by copying `.env.example`.

### macOS / Linux

```bash
cp .env.example .env
```

### Windows (PowerShell)

```powershell
Copy-Item .env.example .env
```

Template contents:

Required variables:

| Variable               | Description                                                   |
|------------------------|---------------------------------------------------------------|
| `YOUTUBE_API_KEY`      | YouTube Data API key (TWIR)                                   |
| `YOUTUBE_PLAYLIST_ID`  | ID of the TWIR YouTube playlist                               |
| `PODBEAN_RSS_FEED`     | Full URL of the Podbean RSS feed for TWIR                    |
| `REDDIT_CLIENT_ID`     | Reddit app client ID (TWIR QoW) — from reddit.com/prefs/apps |
| `REDDIT_CLIENT_SECRET` | Reddit app client secret (TWIR QoW)                           |
| `REDDIT_USERNAME`      | Reddit account username (TWIR QoW)                            |
| `REDDIT_PASSWORD`      | Reddit account password (TWIR QoW)                            |
| `REDDIT_USER_AGENT`    | User-agent string identifying the script to Reddit            |

Optional variables:

| Variable    | Description |
|-------------|-------------|
| `LOG_LEVEL` | Logging verbosity. Valid values are Python logging levels such as `DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL`. Defaults to `INFO` if omitted or invalid. |
| `TEN_P_GEMINI_API_KEY` | Optional Gemini API key used for Ten Pence next-month-game extraction. If omitted, the provider falls back to cache/overrides and `No Game`. |
| `RGDS_SHOW_ID` | Optional Spotify show ID for RGDS. Defaults to the current RGDS show if omitted. |
| `RGDS_REFRESH_TOKEN` | Optional Spotify refresh token for non-interactive RGDS runs. If omitted, first RGDS run uses browser OAuth bootstrap and caches the refresh token under `.cache/RGDS/auth.json`. |

RGDS-required variables (required when running `--podcasts rgds`):

| Variable              | Description |
|-----------------------|-------------|
| `RGDS_CLIENT_ID`      | Spotify app client ID |
| `RGDS_CLIENT_SECRET`  | Spotify app client secret |
| `RGDS_REDIRECT_URI`   | Spotify app redirect URI (must match your Spotify app settings) |

Compatibility note:
- `YOUTUBE_API_KEY` is the canonical TWIR key name.
- `GOOGLE_API_KEY` is still accepted as a legacy fallback for older local `.env` files.

Example `.env`:
```
YOUTUBE_API_KEY=your_youtube_api_key_here
YOUTUBE_PLAYLIST_ID=PLPVR2wA1dpHZR7p2GL5rgB7ybTMxtgPPB
PODBEAN_RSS_FEED=https://feed.podbean.com/TWIR/feed.xml
REDDIT_CLIENT_ID=your_reddit_client_id
REDDIT_CLIENT_SECRET=your_reddit_client_secret
REDDIT_USERNAME=your_reddit_username
REDDIT_PASSWORD=your_reddit_password
REDDIT_USER_AGENT=script:question_search:v1.0 (by u/your_username)
LOG_LEVEL=INFO
TEN_P_GEMINI_API_KEY=your_gemini_api_key_here
RGDS_CLIENT_ID=your_spotify_client_id
RGDS_CLIENT_SECRET=your_spotify_client_secret
RGDS_REDIRECT_URI=http://127.0.0.1:8888/callback
RGDS_SHOW_ID=00sL9tgDezr0PRSzd3C7H6
RGDS_REFRESH_TOKEN=
```

How to get the values:
- `YOUTUBE_API_KEY`: Create in Google Cloud Console and enable YouTube Data API v3 for that project.
- `YOUTUBE_PLAYLIST_ID`: Use the playlist ID from the TWiR YouTube URL (already provided in the example).
- `PODBEAN_RSS_FEED`: Use the RSS feed URL (already provided in the example).
- `REDDIT_*`: Create a Reddit app at https://www.reddit.com/prefs/apps and choose `script`.

RGDS Spotify bootstrap notes:
1. Create a Spotify app in the Spotify Developer Dashboard.
2. Add your redirect URI (for example `http://127.0.0.1:8888/callback`) to the app settings.
3. On first `rgds` run without `RGDS_REFRESH_TOKEN`, a browser OAuth flow is launched.
4. On success, the refresh token is saved to `.cache/RGDS/auth.json` and reused on subsequent runs.

### 2. Centralized env var handling (`env_var_utils.py`)

All environment variables are loaded, validated, and logged in one place via `EnvVarUtils`.

Runtime behavior:
- Required variables are validated at startup; missing required values abort the run.
- Startup logs include all loaded env vars.
- Sensitive values (keys containing `PASSWORD`, `SECRET`, `API_KEY`, `TOKEN`) are masked in logs.
- `LOG_LEVEL` controls application verbosity.
- For TWIR, `YOUTUBE_API_KEY` is preferred and `GOOGLE_API_KEY` is accepted as a fallback alias.
- For Ten Pence AI extraction, invalid/missing `TEN_P_GEMINI_API_KEY` does not fail the run; extraction is disabled for that run and cache/overrides/`No Game` are used.
- For RGDS, `RGDS_CLIENT_ID`, `RGDS_CLIENT_SECRET`, and `RGDS_REDIRECT_URI` are required only when running the RGDS provider.

To create a Reddit app:
1. Go to https://www.reddit.com/prefs/apps
2. Click **Create another app**
3. Select **script** as the type
4. Set the redirect URI to `http://localhost:8080`
5. Copy the client ID (shown under the app name) and secret

---

## Running

### macOS / Linux

```bash
python run_guides.py --podcasts [twir | zttp | ra | 10p | rgds | all]
```

If your venv is not active, run with the venv Python directly:

```bash
./.venv/bin/python run_guides.py --podcasts [twir | zttp | ra | 10p | rgds | all]
./.venv310/bin/python run_guides.py --podcasts [twir | zttp | ra | 10p | rgds | all]
```

### Windows (PowerShell)

```powershell
python run_guides.py --podcasts [twir | zttp | ra | 10p | rgds | all]
```

If your venv is not active:

```powershell
.\.venv\Scripts\python.exe run_guides.py --podcasts [twir | zttp | ra | 10p | rgds | all]
.\.venv310\Scripts\python.exe run_guides.py --podcasts [twir | zttp | ra | 10p | rgds | all]
```

Output files are written to your Desktop:
- `~/Desktop/TWiR Episode Guide.pdf` — the full episode guide PDF
- `~/Desktop/TWiR_Data.csv` — CSV of episode data including questions
- `~/Desktop/ZTTP Episode Guide.pdf` — the ZTTP episode guide PDF
- `~/Desktop/RA Episode Guide.pdf` — the Retro Asylum episode guide PDF
- `~/Desktop/Ten Pence Arcade Episode Guide.pdf` — the Ten Pence Arcade episode guide PDF
- `~/Desktop/RGDS Episode Guide.pdf` — the RGDS episode guide PDF

## Utility Scripts

Convenience scripts are available in `scripts/` for common runs:

```bash
./scripts/zttp.sh   # Runs: python run_guides.py --podcasts zttp
./scripts/twir.sh   # Runs: python run_guides.py --podcasts twir
./scripts/ra.sh     # Runs: python run_guides.py --podcasts ra
./scripts/10p.sh    # Runs: python run_guides.py --podcasts 10p
./scripts/all.sh    # Runs: python run_guides.py --podcasts all
```

If needed, make scripts executable first:

```bash
chmod +x scripts/*.sh
```

## Unified Multi-Podcast Run

Use the shared runner to select one or more podcast guides in a single command.
Each selected podcast generates its own PDF output file (no combined PDF).

CLI selection tokens are lower-case:
- `twir`
- `zttp`
- `ra`
- `10p`
- `rgds`
- `all`

Internally, provider IDs are centralized in `cache_paths.py` as upper-case keys (`TWIR`, `ZTTP`, `RA`, `10P`, `RGDS`) and the runner derives CLI tokens from those constants.

```bash
python run_guides.py --podcasts [twir | zttp | ra | 10p | rgds | all]
python run_guides.py --podcasts zttp
python run_guides.py --podcasts ra
python run_guides.py --podcasts 10p
python run_guides.py --podcasts rgds
python run_guides.py --podcasts twir,zttp
python run_guides.py --podcasts twir,ra
python run_guides.py --podcasts twir,10p
python run_guides.py --podcasts twir,rgds
python run_guides.py --podcasts all
```

If one podcast fails and you still want to continue remaining selections:

```bash
python run_guides.py --podcasts all --continue-on-error
```

---

## Project Structure

```
.
├── run_guides.py            # Unified entry point for TWIR, ZTTP, RA, 10P, and RGDS guide generation
├── data_retriever.py        # Fetches episodes from YouTube API and Podbean RSS feed
├── cache_paths.py           # Centralized cache locations under .cache/<PROVIDER>
├── env_var_utils.py         # Loads and validates environment variables from .env
├── .env.example             # Safe starter template for local configuration
├── requirements.txt         # Runtime dependency list for local installation
├── constants/               # Typed constants registry for provider selection
├── renderers/               # Shared and provider-specific renderers
├── tests/                   # Unit tests
├── podcasts/
│   ├── common/              # Shared base classes, runtime helpers, and constants
│   ├── twir/                # TWIR-specific modules (including qow/)
│   ├── zttp/                # ZTTP-specific modules
│   ├── ra/                  # Retro Asylum–specific modules (scrapes retroasylum.com)
│   │   └── assets/          # Local RA static assets (e.g., RACover.png)
│   ├── tenp/                # Ten Pence Arcade–specific modules
│   └── rgds/                # RGDS-specific modules (Spotify API + OAuth)
├── scripts/                 # Convenience shell scripts (twir.sh, zttp.sh, ra.sh, 10p.sh, all.sh)
├── .env                     # Environment variables (do not commit to source control)
├── .cache/
│   ├── _SHARED/
│   │   └── images/          # Shared image cache reused across providers
│   ├── TWIR/
│   │   ├── images/          # TWIR image cache
│   │   ├── qow_cache.pkl    # TWIR QoW cache file
│   │   └── episodes.json    # TWIR episode metadata cache
│   ├── ZTTP/
│   │   ├── images/          # ZTTP image cache
│   │   ├── episode_cache.pkl
│   │   ├── zzap_cache.pkl
│   │   └── crapverts_cache.pkl
│   ├── RA/
│   │   ├── images/          # RA image cache
│   │   └── episodes_cache.pkl
│   ├── 10P/
│   │   ├── images/          # Ten Pence image cache
│   │   ├── episode_cache.pkl
│   │   └── next_month_game_cache.pkl
│   └── RGDS/
│       ├── images/          # RGDS image cache
│       ├── episodes.json
│       └── auth.json        # Spotify refresh-token cache
└── image_cache/             # Optional manual image staging area (not read automatically)
```

## Logging

The app uses Python's standard `logging` module throughout (instead of `print`).

- Configure verbosity with `LOG_LEVEL` in `.env` (or by exporting it in your shell).
- Severity levels are used consistently:
  - `INFO` for normal progress/status
  - `WARNING` for retries and recoverable issues
  - `ERROR` / `EXCEPTION` for failures

Examples:

```bash
LOG_LEVEL=INFO python run_guides.py --podcasts [twir | zttp | ra | 10p | rgds | all]
LOG_LEVEL=DEBUG python run_guides.py --podcasts [twir | zttp | ra | 10p | rgds | all]
```

---

## Image Cache

Images (episode thumbnails, cover, listen button) are cached on first download and reused on subsequent runs.

Cache locations:
- Provider-local cache: `.cache/<PROVIDER>/images/`
- Shared cross-provider cache: `.cache/_SHARED/images/`

The runtime checks caches in this order:
1. Active provider cache (`.cache/<PROVIDER>/images/`)
2. Shared cache (`.cache/_SHARED/images/`)
3. Other provider caches (cross-provider fallback)
4. Network download

When an image is found in another provider cache, it is copied into shared cache and reused.

This behavior:

- Significantly speeds up generation
- Reduces duplicate downloads across providers
- Allows blocked or unavailable images to be substituted manually

Current standardized cache locations are:
- `.cache/_SHARED/images/`
- `.cache/TWIR/images/`
- `.cache/ZTTP/images/`
- `.cache/RA/images/`
- `.cache/10P/images/`
- `.cache/RGDS/images/`

Cache policy:
- Cache paths are built via shared helpers in `cache_paths.py`.
- Cache directory names are centralized in `cache_paths.py` (`CACHE_DIRNAME`, `IMAGE_CACHE_DIRNAME`).
- Cache filenames are deterministic and URL-derived, so the same image URL maps to the same cache filename across providers.

Cache filenames are derived from the full URL to ensure uniqueness across episodes:
```
https://i.ytimg.com/vi/kE8c463aibw/hqdefault.jpg
  → i-ytimg-com-kE8c463aibw-hqdefault.jpg
```

### Adding images manually

If a download fails, the log will show:
```
Image cache MISS: i-ibb-co-ccL0XZPJ-TWIR-Reddit-logo.jpg - downloading
Image download FAILED for URL: https://i.ibb.co/ccL0XZPJ/TWIR-Reddit-logo.jpg
```

Download the image manually and copy it to the provider image cache directory using the filename from the `Image cache MISS:` line.

Preferred manual-copy locations are:
- `.cache/_SHARED/images/` (recommended for reuse by all providers)
- `.cache/TWIR/images/`
- `.cache/10P/images/`
- `.cache/ZTTP/images/`
- `.cache/RA/images/`

The two static images hosted on `i.ibb.co` (which may be blocked in some environments) are:

| Cache filename                       | Source URL                                          |
|--------------------------------------|-----------------------------------------------------|
| `i-ibb-co-ccL0XZPJ-TWIR-Reddit-logo.jpg` | `https://i.ibb.co/ccL0XZPJ/TWIR-Reddit-logo.jpg` |
| `i-ibb-co-NWmMHcH-Listen-Now.jpg`        | `https://i.ibb.co/NWmMHcH/Listen-Now.jpg`        |

---

## Ten Pence AI Extraction

Ten Pence uses AI only for next-month-game extraction, and only when there is no override/cached value.

Resolution order per episode:
1. Existing next-month-game cache value
2. Hardcoded override in `podcasts/tenp/page_constants.py`
3. Gemini extraction (if `TEN_P_GEMINI_API_KEY` is configured and valid)
4. Fallback value `No Game`

Failure handling:
- Missing key: AI is skipped, run continues.
- Invalid key/API errors: AI is disabled for the rest of the run and processing continues.
- Any extraction exception: warning is logged and fallback is used.

The run never fails solely because Gemini extraction fails.

---

## Developer Notes

### Test mode

Use environment variables to run a short test selection (default count is 5):

```bash
GUIDE_TEST_RUN=true GUIDE_TEST_COUNT=5 python run_guides.py --podcasts [twir | zttp | ra | 10p | all]
```

### QoW cache

Reddit QoW data is cached in `.cache/TWIR/qow_cache.pkl`. Deleting it will cause the next run to re-scrape all posts from Reddit. The cache contains no credentials.

### Episode retry logic

If an exception occurs while building an episode page, the TWIR builder retries based on `RETRY_NUMBER` (currently `1`, so one retry after the first failure) before aborting. This helps with transient network/image errors.

### Shared main/runtime flow

Provider entrypoints use shared helpers from `podcasts/common/` (TWIR, ZTTP, RA, and 10P):
- `runtime.py` for logging bootstrap and test-run env parsing
- `guide_main_base.py` for common create/write/save orchestration

### Retro Asylum (RA) specifics

- **Data source**: RA episodes are scraped from `retroasylum.com` (no API keys required). An active internet connection is needed on the first run; subsequent runs use the local cache.
- **Cover asset**: The RA cover image is stored locally at `podcasts/ra/assets/RACover.png`.
- **Episode filtering**: Episodes whose cover image URL ends with `RA_error.png` are suppressed in both the TOC and episode pages. The filter list is configurable via `TEXT_TO_REMOVE` in `podcasts/ra/page_constants.py`.
- **Cache behavior**: The generator reads and writes only provider-local cache paths under `.cache/<PROVIDER>/`.
- **Network resilience**: If `retroasylum.com` is unreachable during page discovery, the generator falls back to the existing episode cache rather than aborting.

---

## Unit Tests

The project uses Python's built-in `unittest` framework with tests in the `tests/` directory.

Run all tests:

### macOS / Linux

```bash
python -m unittest discover -s tests -v
```

If using the local venv directly:

```bash
./.venv/bin/python -m unittest discover -s tests -v
./.venv310/bin/python -m unittest discover -s tests -v
```

Run a single test module:

```bash
python -m unittest tests.test_twir_utils -v
./.venv310/bin/python -m unittest tests.test_twir_utils -v
```

### Windows (PowerShell)

```powershell
python -m unittest discover -s tests -v
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
.\.venv310\Scripts\python.exe -m unittest discover -s tests -v
```

Run a single test case or method:

```bash
python -m unittest tests.test_twir_utils.TestExtractEpisodeNumber -v
python -m unittest tests.test_twir_utils.TestExtractEpisodeNumber.test_twir_ep_format -v
./.venv310/bin/python -m unittest tests.test_twir_utils.TestExtractEpisodeNumber -v
./.venv310/bin/python -m unittest tests.test_twir_utils.TestExtractEpisodeNumber.test_twir_ep_format -v
```

Current test coverage includes:
- `podcasts.twir.twir_utils` parsing helpers
- `podcasts.twir.pdf_writer` cache key/sanitization and text splitting helpers
- `podcasts.twir.qow` model and cache loading behavior
- `podcasts.ra.episode` episode number extraction (standard and Bytesize formats)
- `podcasts.ra.pdf_writer` episode filtering logic
- constants registry and ZTTP caching flows

---

## Dependencies

| Package          | Purpose                                              |
|------------------|------------------------------------------------------|
| `python-dotenv`  | Load `.env` file into the environment                |
| `python-youtube` | YouTube Data API v3 client (imported as `pyyoutube`) |
| `feedparser`     | Parse the Podbean RSS feed                           |
| `requests`       | HTTP image downloads                                 |
| `Pillow`         | Image processing and resizing                        |
| `reportlab`      | PDF generation                                       |
| `numpy`          | Image array conversion for JPEG→PNG normalisation    |
| `praw`           | Reddit API client for QoW scraping                   |
| `beautifulsoup4` | HTML parsing for ZTTP page and content extraction    |
| `lxml`           | Parser backend used by BeautifulSoup in ZTTP flows   |

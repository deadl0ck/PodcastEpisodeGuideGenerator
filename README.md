# Podcast Episode Guide Generator

Generates PDF "magazine-style" episode guides for:
- [This Week in Retro (TWIR)](https://www.youtube.com/@ThisWeekinRetro/videos)
- [Zapped to the Past (ZTTP)](https://zappedtothepast.com/)

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
- [Unified Multi-Podcast Run](#unified-multi-podcast-run)
- [Project Structure](#project-structure)
- [Logging](#logging)
- [Image Cache](#image-cache)
- [Developer Notes](#developer-notes)
- [Unit Tests](#unit-tests)
- [Dependencies](#dependencies)

---

## Prerequisites

- Python 3.9 or later (tested on 3.9 and 3.10)
- A **Google API key** with the YouTube Data API v3 enabled (TWIR)
- A **Reddit account** with a registered script application (TWIR QoW scraping)

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
pip install python-dotenv python-youtube feedparser numpy requests Pillow reportlab praw

# 4) Create .env from the example in this README

# 5) Run the app
python run_guides.py --podcasts twir
```

### Windows (PowerShell)

```powershell
# 1) Open PowerShell and go to the project folder
cd C:\path\to\PodcastEpisoideGuideGenerator

# 2) Create and activate a virtual environment
py -3 -m venv .venv
.\.venv\Scripts\Activate.ps1

# 3) Install dependencies
pip install python-dotenv python-youtube feedparser numpy requests Pillow reportlab praw

# 4) Create .env from the example in this README

# 5) Run the app
python run_guides.py --podcasts twir
```

Output files are written to your Desktop (podcast dependent):
- `TWiR Episode Guide.pdf`
- `TWiR_Data.csv`
- `ZTTP Episode Guide.pdf`

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
pip install python-dotenv python-youtube feedparser numpy requests Pillow reportlab praw
```

### Windows (PowerShell)

```powershell
py -3 -m venv .venv
.\.venv\Scripts\Activate.ps1
python --version
pip install python-dotenv python-youtube feedparser numpy requests Pillow reportlab praw
```

Optional: if you specifically want to pin to Python 3.10 (known-good version):

### macOS / Linux (Python 3.10 pinned)

```bash
python3.10 -m venv .venv310
source .venv310/bin/activate
python --version                      # Should show Python 3.10.x
pip install python-dotenv python-youtube feedparser numpy requests Pillow reportlab praw
```

### Windows (PowerShell, Python 3.10 pinned)

```powershell
py -3.10 -m venv .venv310
.\.venv310\Scripts\Activate.ps1
python --version
pip install python-dotenv python-youtube feedparser numpy requests Pillow reportlab praw
```

If `python3.10` is not available, you can still create a venv with your installed Python 3.x version.

> **Note:** The YouTube client library is imported as `from pyyoutube import Api` but the pip package name is `python-youtube`.

---

## Configuration

### 1. `.env` file

Create a `.env` file in the project root (copy the template below).

Required variables:

| Variable               | Description                                                   |
|------------------------|---------------------------------------------------------------|
| `GOOGLE_API_KEY`       | Google API key with the YouTube Data API v3 enabled (TWIR)   |
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

Example `.env`:
```
GOOGLE_API_KEY=your_google_api_key_here
YOUTUBE_PLAYLIST_ID=PLPVR2wA1dpHZR7p2GL5rgB7ybTMxtgPPB
PODBEAN_RSS_FEED=https://feed.podbean.com/TWIR/feed.xml
REDDIT_CLIENT_ID=your_reddit_client_id
REDDIT_CLIENT_SECRET=your_reddit_client_secret
REDDIT_USERNAME=your_reddit_username
REDDIT_PASSWORD=your_reddit_password
REDDIT_USER_AGENT=script:question_search:v1.0 (by u/your_username)
LOG_LEVEL=INFO
```

How to get the values:
- `GOOGLE_API_KEY`: Create in Google Cloud Console and enable YouTube Data API v3 for that project.
- `YOUTUBE_PLAYLIST_ID`: Use the playlist ID from the TWiR YouTube URL (already provided in the example).
- `PODBEAN_RSS_FEED`: Use the RSS feed URL (already provided in the example).
- `REDDIT_*`: Create a Reddit app at https://www.reddit.com/prefs/apps and choose `script`.

### 2. Centralized env var handling (`env_var_utils.py`)

All environment variables are loaded, validated, and logged in one place via `EnvVarUtils`.

Runtime behavior:
- Required variables are validated at startup; missing required values abort the run.
- Startup logs include all loaded env vars.
- Sensitive values (keys containing `PASSWORD`, `SECRET`, `API_KEY`, `TOKEN`) are masked in logs.
- `LOG_LEVEL` controls application verbosity.

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
python run_guides.py --podcasts twir
```

If your venv is not active, run with the venv Python directly:

```bash
./.venv/bin/python run_guides.py --podcasts twir
./.venv310/bin/python run_guides.py --podcasts twir
```

### Windows (PowerShell)

```powershell
python run_guides.py --podcasts twir
```

If your venv is not active:

```powershell
.\.venv\Scripts\python.exe run_guides.py --podcasts twir
.\.venv310\Scripts\python.exe run_guides.py --podcasts twir
```

Output files are written to your Desktop:
- `~/Desktop/TWiR Episode Guide.pdf` — the full episode guide PDF
- `~/Desktop/TWiR_Data.csv` — CSV of episode data including questions

## Unified Multi-Podcast Run

Use the shared runner to select one or more podcast guides in a single command.
Each selected podcast generates its own PDF output file (no combined PDF).

```bash
python run_guides.py --podcasts twir
python run_guides.py --podcasts zttp
python run_guides.py --podcasts twir,zttp
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
├── run_guides.py            # Unified entry point for TWIR and ZTTP guide generation
├── data_retriever.py        # Fetches episodes from YouTube API and Podbean RSS feed
├── cache_paths.py           # Centralized cache locations under .cache/TWIR and .cache/ZTTP
├── env_var_utils.py         # Loads and validates environment variables from .env
├── constants/               # Typed constants registry for provider selection
├── renderers/               # Shared and provider-specific renderers
├── tests/                   # Unit tests
├── podcasts/
│   ├── common/              # Shared base classes, runtime helpers, and constants
│   ├── twir/                # TWIR-specific modules (including qow/)
│   └── zttp/                # ZTTP-specific modules
├── .env                     # Environment variables (do not commit to source control)
├── .cache/
│   ├── TWIR/
│   │   ├── images/          # TWIR image cache
│   │   ├── qow_cache.pkl    # TWIR QoW cache file
│   │   └── episodes.json    # Reserved for future TWIR episode metadata cache
│   └── ZTTP/
│       ├── images/          # ZTTP image cache
│       ├── episode_cache.pkl
│       ├── zzap_cache.pkl
│       └── crapverts_cache.pkl
└── image_cache/             # Legacy image cache path (still read for migration)
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
LOG_LEVEL=INFO python run_guides.py --podcasts twir
LOG_LEVEL=DEBUG python run_guides.py --podcasts twir
```

---

## Image Cache

Images (episode thumbnails, cover, listen button) are cached in `image_cache/` on first download. Subsequent runs use the local copy, which:

- Significantly speeds up generation
- Allows blocked or unavailable images to be substituted manually

Current standardized cache locations are:
- `.cache/TWIR/images/`
- `.cache/ZTTP/images/`
Legacy files in `image_cache/` are still detected and migrated automatically.

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

Download the image manually and copy it to `image_cache/` using the filename from the `Image cache MISS:` line.

Preferred location for manual copies is now `.cache/TWIR/images/`.

The two static images hosted on `i.ibb.co` (which may be blocked in some environments) are:

| Cache filename                       | Source URL                                          |
|--------------------------------------|-----------------------------------------------------|
| `i-ibb-co-ccL0XZPJ-TWIR-Reddit-logo.jpg` | `https://i.ibb.co/ccL0XZPJ/TWIR-Reddit-logo.jpg` |
| `i-ibb-co-NWmMHcH-Listen-Now.jpg`        | `https://i.ibb.co/NWmMHcH/Listen-Now.jpg`        |

---

## Developer Notes

### Test mode

Use environment variables to run a short test selection (default count is 5):

```bash
GUIDE_TEST_RUN=true GUIDE_TEST_COUNT=5 python run_guides.py --podcasts twir
```

### QoW cache

Reddit QoW data is cached in `.cache/TWIR/qow_cache.pkl`. Deleting it will cause the next run to re-scrape all posts from Reddit. The cache contains no credentials.

### Episode retry logic

If an exception occurs while building an episode page, the TWIR builder retries based on `RETRY_NUMBER` (currently `1`, so one retry after the first failure) before aborting. This helps with transient network/image errors.

### Shared main/runtime flow

Both provider entrypoints (`podcasts/twir/main.py` and `podcasts/zttp/main.py`) now use shared helpers from `podcasts/common/`:
- `runtime.py` for logging bootstrap and test-run env parsing
- `guide_main_base.py` for common create/write/save orchestration

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

# Refactoring Plan

Each step is a focused, independently reviewable change. Steps are ordered so each is safe to apply without any later step.

---

## Step 1 — Add `_EPISODE_SEPARATOR` to base renderer

**Why:** The string `"[ ---------- Building Episode ---------- ]"` is copy-pasted in all 5 renderers. A single class constant removes the duplication.

**Files changed:**
- `renderers/episode_renderer_base.py` — add `_EPISODE_SEPARATOR = "[ ---------- Building Episode ---------- ]"` as a class attribute on `BaseEpisodeRenderer`
- `renderers/ra_episode_renderer.py:72` — replace literal with `self._EPISODE_SEPARATOR`
- `renderers/twir_episode_renderer.py:115` — replace literal with `self._EPISODE_SEPARATOR`
- `renderers/zttp_episode_renderer.py:127` — replace literal with `self._EPISODE_SEPARATOR`
- `renderers/tenp_episode_renderer.py:28` — replace literal with `self._EPISODE_SEPARATOR`
- `renderers/rgds_episode_renderer.py:71` — replace literal with `self._EPISODE_SEPARATOR`

---

## Step 2 — Remove dead `split_into_multiline` wrappers from 4 provider PDF writers

**Why:** RA, ZTTP, TenP, and RGDS each define a static `split_into_multiline` that is an exact pass-through to `BasePDFWriter.split_into_multiline` with the same default (90 chars = the base class default). None of these wrappers are called from outside their own class — they are pure dead code.

**Files changed:**
- `podcasts/ra/pdf_writer.py` — remove `split_into_multiline` static method; remove `SUB_HEADINGS_LETTERS_PER_LINE` from imports (only used by that method)
- `podcasts/zttp/pdf_writer.py` — remove `split_into_multiline` static method; remove `SUB_HEADINGS_LETTERS_PER_LINE` from imports
- `podcasts/tenp/pdf_writer.py` — remove `split_into_multiline` static method; remove `SUB_HEADINGS_LETTERS_PER_LINE` from imports
- `podcasts/rgds/pdf_writer.py` — remove `split_into_multiline` static method; remove `SUB_HEADINGS_LETTERS_PER_LINE` from imports

**Note:** TWIR's wrapper is handled separately in Step 3 because it has a different default (92 vs 90) and is called internally.

---

## Step 3 — Remove TWIR `split_into_multiline` wrapper; update internal callers

**Why:** TWIR's wrapper uses `DEFAULT_LETTERS_PER_LINE = 92` as its default, but is only called in two places inside the same class (both without a count argument). Those two call sites can just pass the count explicitly, making the wrapper redundant. External callers (the TWIR episode renderer) already pass an explicit count so they are unaffected.

**Files changed:**
- `podcasts/twir/pdf_writer.py:34-36` — remove the `split_into_multiline` static method
- `podcasts/twir/pdf_writer.py:39` — change `PDFWriter.split_into_multiline(text)` → `BasePDFWriter.split_into_multiline(text, DEFAULT_LETTERS_PER_LINE)`
- `podcasts/twir/pdf_writer.py:98` — change `PDFWriter.split_into_multiline(...)` → `BasePDFWriter.split_into_multiline(..., DEFAULT_LETTERS_PER_LINE)`

**Tests:** `tests/test_pdf_writer.py` calls `PDFWriter.split_into_multiline` — this resolves to the inherited `BasePDFWriter.split_into_multiline` via Python inheritance, so tests continue to pass unchanged.

---

## Step 4 — Remove backward-compat aliases from ZTTP PDF writer

**Why:** `insert_image_from_ulr_centred` and `insert_image_from_ulr_with_link` (note: typo in the original names) are labelled "Backward-compatible aliases during migration". grep confirms they are not called from anywhere in the codebase — the migration is done.

**Files changed:**
- `podcasts/zttp/pdf_writer.py:54-62` — delete the two alias methods

---

## Step 5 — Remove RA's redundant `write_jump_to_toc_link`

**Why:** `RAEpisodeRenderer` calls `writer.write_jump_to_toc_link()`, which is a method defined on `RA.PDFWriter`. That method is identical in behaviour to the inherited `BasePDFWriter.insert_jump_to_toc_link()` — both write `"[Jump to TOC]"` using `self._jump_to_toc_font` (= `DEFAULT_FONT_BOLD` for RA) and `self._toc_bookmark` (= `"TOC"` for RA). All other renderers already call `insert_jump_to_toc_link()` directly.

**Files changed:**
- `podcasts/ra/pdf_writer.py` — remove `write_jump_to_toc_link` method; clean up now-unused imports: `JUMP_TO_TOC_TEXT`, `SUBTLE_TEXT_COLOUR`, `TOC_FONT_SIZE`
- `renderers/ra_episode_renderer.py:66` — change `writer.write_jump_to_toc_link()` → `writer.insert_jump_to_toc_link()`

---

## Step 6 — Fix `ensure_cache_dirs()` in RA and ZTTP page_constants

**Why:** RA and ZTTP define `ensure_cache_dirs()` with two inline `os.makedirs` calls. TenP and RGDS already delegate to `cache_paths.ensure_podcast_cache_dirs(PROVIDER_KEY)`, which does the same thing. RA and ZTTP should do the same for consistency.

**Files changed:**
- `podcasts/ra/page_constants.py` — add `ensure_podcast_cache_dirs` to `cache_paths` imports; replace body of `ensure_cache_dirs()` with `ensure_podcast_cache_dirs(RA_PROVIDER_KEY)`
- `podcasts/zttp/page_constants.py` — add `ensure_podcast_cache_dirs` to `cache_paths` imports; replace body of `ensure_cache_dirs()` with `ensure_podcast_cache_dirs(ZTTP_PROVIDER_KEY)`

---

## Step 7 — Remove dead code from ZTTP html_utils

**Why:** `podcasts/zttp/html_utils.py` defines `get_all_pages` and `get_details`. Neither method is called from anywhere in the ZTTP codebase — ZTTP's actual callers (`crapverts.py`, `covers.py`) only use the inherited `get_html_from_url`. The ZTTP class body is entirely dead code.

**Files changed:**
- `podcasts/zttp/html_utils.py` — remove `get_all_pages` and `get_details`; leave `class HTMLUtils(BaseHTMLUtils): pass` so existing imports in `crapverts.py` and `covers.py` continue to work

---

## Step 8 — Move `format_duration` to `ZzapUtils`

**Why:** `format_duration` is a free function in `zttp/main.py` that converts a raw seconds string to `HH:MM`. It is a utility function, not orchestration logic, so it belongs in `ZzapUtils`.

**Files changed:**
- `podcasts/zttp/zzap_utils.py` — add `@staticmethod format_duration(duration_str: str) -> str` to `ZzapUtils`
- `podcasts/zttp/main.py` — remove the `format_duration` function definition; update the one call site (`format_duration(ep.itunes_duration)`) to `ZzapUtils.format_duration(ep.itunes_duration)`

---

## Step 9 — Move `_format_duration_ms` to `RGDSTextUtils`

**Why:** `_format_duration_ms` is a free function in `rgds/main.py` that converts Spotify's millisecond duration to `HH:MM:SS`. It is a text/formatting utility, not orchestration, so it belongs in `RGDSTextUtils`.

**Note on Steps 8 & 9:** These two functions do similar things (format a duration) but differ in input type (string seconds vs int milliseconds) and output format (`HH:MM` vs `HH:MM:SS`) because the source data formats differ. Merging them into a single shared function would require flags for both input unit and output format — not worth it.

**Files changed:**
- `podcasts/rgds/text_utils.py` — add `@staticmethod format_duration_ms(duration_ms: int | None) -> str` to `RGDSTextUtils`
- `podcasts/rgds/main.py` — remove the `_format_duration_ms` function definition; update the one call site to `RGDSTextUtils.format_duration_ms(...)`

---

## Step 10 — Inline `episode_page_builder.py` into `twir/main.py`

**Why:** `podcasts/twir/episode_page_builder.py` is a 17-line file containing a single function whose entire body is two lines: create a renderer, call it. The indirection adds no value.

**Files changed:**
- `podcasts/twir/main.py:build_pages` — replace `build_episode_pages(self.writer, episodes, context["qow"], RETRY_NUMBER)` with the two lines inline: `renderer = TWIREpisodeRenderer(qow_dict=context["qow"], retry_number=RETRY_NUMBER)` / `renderer.render_episode_pages(self.writer, episodes)`; add the `TWIREpisodeRenderer` import directly; remove the `build_episode_pages` import
- `podcasts/twir/episode_page_builder.py` — delete the file

---

## Step 11 — Fix pre-existing `praw` import error in tests

**Why:** `tests/test_qow.py` fails at import time with `ModuleNotFoundError: No module named 'praw'` because the `praw` package is not installed in the dev/test environment. This masks any real test failure in that module.

**Options (pick one):**
- A) Install `praw` into the venv: `pip install praw` (and add to `requirements.txt` if missing)
- B) Guard the test import so the module is skipped when `praw` is absent:
  ```python
  import unittest
  try:
      import praw
  except ImportError:
      raise unittest.SkipTest("praw not installed")
  ```

**Files changed (option B):**
- `tests/test_qow.py` — add the skip guard at the top of the file

---

## Summary Table

| Step | What | Why |
|------|------|-----|
| 1 | Add `_EPISODE_SEPARATOR` constant to base renderer | 5-way copy-paste of log string |
| 2 | Remove 4 dead `split_into_multiline` wrappers (RA/ZTTP/TenP/RGDS) | Not called from anywhere; pass-through to base default |
| 3 | Remove TWIR `split_into_multiline` wrapper; inline callers | Only 2 internal callers; both can pass count explicitly |
| 4 | Remove ZTTP backward-compat aliases | Migration done; not called from anywhere |
| 5 | Remove RA's `write_jump_to_toc_link` | Identical to inherited `insert_jump_to_toc_link` |
| 6 | Fix RA/ZTTP `ensure_cache_dirs` to delegate | TenP/RGDS already do this; removes inline `os.makedirs` duplication |
| 7 | Remove dead code from ZTTP `html_utils` | `get_all_pages`/`get_details` never called in ZTTP |
| 8 | Move `format_duration` to `ZzapUtils` | Free function in main; belongs in utils |
| 9 | Move `_format_duration_ms` to `RGDSTextUtils` | Free function in main; belongs in utils |
| 10 | Inline `episode_page_builder.py` | 17-line file wrapping 2 lines of code |
| 11 | Fix `praw` import error in `tests/test_qow.py` | Pre-existing test failure; `praw` not installed in dev env |

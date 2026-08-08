"""
fastdl_downloader.py — Headless Instagram video downloader via fastdl.app.

Uses Playwright (headless Chromium) to load fastdl.app, submit the URL,
extract the signed mp4 link, and stream it to disk.
No Instagram account, no cookies, no IPC bridge needed.

Requires: pip install playwright && python -m playwright install chromium
"""

import asyncio
import json
import re
import time
from pathlib import Path

import requests

_BASE        = Path(__file__).parent
REQUEST_FILE = _BASE / "temp" / "dl_request.json"
RESULT_FILE  = _BASE / "temp" / "dl_result.json"
TIMEOUT_IPC  = 360

_DL_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/124 Safari/537.36",
    "Referer": "https://fastdl.app/",
}


def _normalize_ig_url(url: str) -> str:
    m = re.search(r'/(reel|p|tv)/([A-Za-z0-9_-]+)', url)
    if m:
        return f"https://www.instagram.com/p/{m.group(2)}/"
    return url.split("?")[0]


async def _get_mp4_url(ig_url: str) -> str:
    from playwright.async_api import async_playwright
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        try:
            await page.goto("https://fastdl.app/en4", wait_until="networkidle", timeout=20000)
            await page.fill("#search-form-input", ig_url)
            await page.click("#searchFormButton")
            await page.wait_for_selector("a[href*='media.fastdl.app']", timeout=20000)
            link = await page.get_attribute("a[href*='media.fastdl.app']", "href")
            return link
        finally:
            await browser.close()


def _download_with_playwright(ig_url: str, output_path: str, progress_cb=None) -> str:
    if progress_cb:
        progress_cb("Fetching download link (headless browser)...")

    mp4_url = asyncio.run(_get_mp4_url(ig_url))
    if not mp4_url:
        raise RuntimeError("fastdl.app returned no download link")

    if progress_cb:
        progress_cb("Downloading video...")

    with requests.get(mp4_url, headers=_DL_HEADERS, stream=True, timeout=180) as r:
        r.raise_for_status()
        with open(output_path, "wb") as f:
            for chunk in r.iter_content(65536):
                f.write(chunk)

    size = Path(output_path).stat().st_size
    if size < 10_000:
        raise RuntimeError(f"Downloaded file too small ({size} bytes)")
    return output_path


def download_via_fastdl(ig_url: str, output_path: str, progress_cb=None) -> str:
    ig_url = _normalize_ig_url(ig_url)
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)

    # ── Playwright (headless Chromium, no credentials needed) ─────────────────
    try:
        return _download_with_playwright(ig_url, output_path, progress_cb)
    except Exception as e:
        print(f"[fastdl] Playwright failed: {e} — falling back to IPC bridge")

    # ── IPC bridge fallback (Claude Code in-app browser) ─────────────────────
    if progress_cb:
        progress_cb("Playwright failed — waiting for Claude Code download agent...")

    tmp = _BASE / "temp"
    tmp.mkdir(exist_ok=True)
    REQUEST_FILE.unlink(missing_ok=True)
    RESULT_FILE.unlink(missing_ok=True)
    REQUEST_FILE.write_text(json.dumps({"url": ig_url, "output": str(output_path)}))

    deadline = time.time() + TIMEOUT_IPC
    while time.time() < deadline:
        if RESULT_FILE.exists():
            try:
                result = json.loads(RESULT_FILE.read_text(encoding="utf-8-sig"))
            except json.JSONDecodeError:
                time.sleep(0.5)
                continue
            RESULT_FILE.unlink(missing_ok=True)
            REQUEST_FILE.unlink(missing_ok=True)
            if result.get("error"):
                raise RuntimeError(result["error"])
            return result["path"]
        time.sleep(2)

    REQUEST_FILE.unlink(missing_ok=True)
    raise RuntimeError(f"Download timed out after {TIMEOUT_IPC}s")

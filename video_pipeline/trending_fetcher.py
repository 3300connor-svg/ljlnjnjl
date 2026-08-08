"""
trending_fetcher.py — Fetch top 50 trending TikTok/Reels sounds and cache locally.

Source: TikTok Creative Center trending music API (no auth required).
Falls back to YouTube search + yt-dlp download if direct TikTok audio fails.
Cache refreshes every 24h automatically.
"""

import json
import os
import time
import subprocess
from pathlib import Path

import requests

from config import TRENDING_AUDIO_DIR

CACHE_FILE    = str(Path(TRENDING_AUDIO_DIR) / "_trending_cache.json")
CACHE_TTL     = 86400   # 24 hours
ITUNES_API    = "https://itunes.apple.com/us/rss/topsongs/limit=50/json"


def _load_cache() -> list[dict]:
    try:
        with open(CACHE_FILE) as f:
            data = json.load(f)
        if time.time() - data.get("fetched_at", 0) < CACHE_TTL:
            return data.get("tracks", [])
    except Exception:
        pass
    return []


def _save_cache(tracks: list[dict]):
    Path(TRENDING_AUDIO_DIR).mkdir(parents=True, exist_ok=True)
    with open(CACHE_FILE, "w") as f:
        json.dump({"fetched_at": time.time(), "tracks": tracks}, f, indent=2)


def fetch_trending_list(force_refresh: bool = False) -> list[dict]:
    """
    Return list of dicts: {title, artist}
    Source: iTunes Top 50. Cached 24h.
    """
    if not force_refresh:
        cached = _load_cache()
        if cached:
            return cached

    try:
        r = requests.get(ITUNES_API, timeout=15)
        r.raise_for_status()
        entries = r.json().get("feed", {}).get("entry", [])
        tracks = []
        for entry in entries:
            title  = entry.get("im:name",   {}).get("label", "")
            artist = entry.get("im:artist", {}).get("label", "")
            if title:
                tracks.append({"title": title, "artist": artist})
        if tracks:
            _save_cache(tracks)
            return tracks
    except Exception as e:
        print(f"[trending] iTunes fetch failed: {e}")

    return _load_cache()


def download_track(track: dict) -> str | None:
    """
    Download audio for a track dict. Tries TikTok URL first, then YouTube search.
    Returns local .mp3 path or None on failure.
    """
    Path(TRENDING_AUDIO_DIR).mkdir(parents=True, exist_ok=True)
    safe_name  = "".join(c for c in f"{track['title']} - {track['artist']}" if c.isalnum() or c in " -_")[:60]
    dest_base  = str(Path(TRENDING_AUDIO_DIR) / safe_name)
    dest_mp3   = dest_base + ".mp3"

    if Path(dest_mp3).exists():
        return dest_mp3

    # Try TikTok music page
    if track.get("tiktok_url"):
        try:
            subprocess.run(
                ["yt-dlp", "-x", "--audio-format", "mp3", "--audio-quality", "0",
                 "-o", dest_base + ".%(ext)s", "--no-warnings", "--quiet",
                 track["tiktok_url"]],
                check=True, timeout=60, capture_output=True,
            )
            if Path(dest_mp3).exists():
                return dest_mp3
        except Exception:
            pass

    # Fallback: YouTube search
    search_q   = f"ytsearch1:{track['title']} {track['artist']} official audio"
    try:
        subprocess.run(
            ["yt-dlp", "-x", "--audio-format", "mp3", "--audio-quality", "0",
             "-o", dest_base + ".%(ext)s", "--no-warnings", "--quiet",
             "--match-filter", "duration < 600",
             search_q],
            check=True, timeout=90, capture_output=True,
        )
        if Path(dest_mp3).exists():
            return dest_mp3
    except Exception as e:
        print(f"[trending] YouTube fallback failed for '{track['title']}': {e}")

    return None


def get_random_trending(top_n: int = 20) -> tuple[dict, str] | tuple[None, None]:
    """
    Pick a random track from the top_n trending, download it, return (track_dict, local_path).
    Returns (None, None) if nothing available.
    """
    import random
    tracks = fetch_trending_list()
    if not tracks:
        return None, None

    pool = tracks[:top_n]
    random.shuffle(pool)

    for track in pool:
        path = download_track(track)
        if path:
            return track, path

    return None, None

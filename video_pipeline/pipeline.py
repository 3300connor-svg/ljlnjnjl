"""
pipeline.py — Full single-video processing chain.

download → upload-for-wavespeed → face swap → audio mix → post-process
Returns dict: {path, audio_name} or None on failure.
"""

import os
import time
import uuid
from pathlib import Path

import random

from config import WAVESPEED_API_KEY, OUTPUT_DIR, TEMP_DIR
from downloader import download_video, upload_temp
from wavespeed_video import WaveSpeedVideoClient, WaveSpeedVideoError
from trending_fetcher import fetch_trending_list
from post_process import post_process


def _tmp(suffix: str) -> str:
    Path(TEMP_DIR).mkdir(parents=True, exist_ok=True)
    return str(Path(TEMP_DIR) / f"{uuid.uuid4().hex[:8]}{suffix}")


def run_pipeline(source_url: str, progress_cb=None, clothes_prompt: str = "") -> dict | None:
    """
    Full pipeline for a single video URL.

    Returns dict: {path: str, audio_name: str} or None on failure.
    """
    cb = progress_cb or (lambda m: print(f"  {m}"))

    raw_path  = _tmp("_raw.mp4")
    swap_path = _tmp("_swap.mp4")
    slug      = source_url.rstrip("/").split("/")[-1][:30]
    out_path   = str(Path(OUTPUT_DIR) / f"{slug}_{int(time.time())}.mp4")
    Path(OUTPUT_DIR).mkdir(parents=True, exist_ok=True)

    try:
        cb("Downloading source video...")
        download_video(source_url, raw_path)
        cb(f"Downloaded ({Path(raw_path).stat().st_size // 1024} KB)")

        cb("Uploading to temp host...")
        public_url = upload_temp(raw_path)
        cb(f"Hosted: {public_url}")

        client = WaveSpeedVideoClient(WAVESPEED_API_KEY)
        client.face_swap(public_url, swap_path, progress_cb=cb)
        cb(f"Face swap complete ({Path(swap_path).stat().st_size // 1024} KB)")

        # Optional clothes swap step
        if clothes_prompt.strip():
            clothes_path = _tmp("_clothes.mp4")
            cb("Uploading face-swapped video for clothes edit...")
            swap_public_url = upload_temp(swap_path)
            client.video_edit(swap_public_url, clothes_prompt, clothes_path, progress_cb=cb)
            Path(swap_path).unlink(missing_ok=True)
            swap_path = clothes_path

        # Pick a trending track name — user adds it manually on Instagram
        tracks = fetch_trending_list()
        if tracks:
            track = random.choice(tracks[:20])
            audio_name = f"{track['title']} — {track['artist']}" if track.get("artist") else track["title"]
        else:
            audio_name = None

        post_process(swap_path, out_path, progress_cb=cb)
        cb(f"Done → {out_path}")

        return {"path": out_path, "audio_name": audio_name}

    except WaveSpeedVideoError as e:
        cb(f"WaveSpeed error: {e}")
        return None
    except Exception as e:
        cb(f"Pipeline error: {e}")
        return None
    finally:
        for p in [raw_path, swap_path]:
            try:
                Path(p).unlink(missing_ok=True)
            except Exception:
                pass

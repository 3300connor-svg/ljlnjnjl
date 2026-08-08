"""
downloader.py — fastdl.app downloader + public URL hosting via Catbox.

  download_video()     → saves mp4 locally via fastdl.app
  upload_catbox()      → catbox.moe (permanent); falls back to litterbox (24h)
  get_video_duration() → video duration in seconds via ffprobe
  trim_video()         → trims video to max_seconds using ffmpeg
  download_url()       → stream-download any URL to a local path
"""

import mimetypes
import subprocess
import requests
from pathlib import Path

from config import TEMP_DIR


def download_video(source_url: str, output_path: str, progress_cb=None) -> str:
    from fastdl_downloader import download_via_fastdl
    if progress_cb:
        progress_cb("Downloading via fastdl.app...")
    return download_via_fastdl(source_url, output_path, progress_cb=progress_cb)


def upload_catbox(local_path: str, on_fallback=None, progress_cb=None) -> str:
    """Upload to catbox.moe (permanent, anonymous)."""
    fname = Path(local_path).name
    mime  = mimetypes.guess_type(local_path)[0] or "application/octet-stream"
    if progress_cb:
        progress_cb(f"Uploading {fname} to Catbox...")
    with open(local_path, "rb") as f:
        r = requests.post(
            "https://catbox.moe/user/api.php",
            data={"reqtype": "fileupload", "userhash": ""},
            files={"fileToUpload": (fname, f, mime)},
            timeout=300,
        )
    r.raise_for_status()
    url = r.text.strip()
    if url.startswith("https://"):
        return url
    raise RuntimeError(f"Unexpected catbox response: {url[:120]}")


def get_video_duration(video_path: str) -> float:
    import re
    result = subprocess.run(
        ["ffmpeg", "-i", video_path],
        capture_output=True, text=True,
    )
    m = re.search(r"Duration:\s*(\d+):(\d+):([\d.]+)", result.stderr)
    if m:
        h, mn, s = int(m.group(1)), int(m.group(2)), float(m.group(3))
        return h * 3600 + mn * 60 + s
    return 0.0


def trim_video(input_path: str, output_path: str, max_seconds: int = 30) -> str:
    """
    Trim to max_seconds if video is longer.
    Returns output_path if trimmed, input_path if already short enough.
    """
    duration = get_video_duration(input_path)
    if duration <= max_seconds:
        return input_path
    subprocess.run(
        ["ffmpeg", "-y", "-i", input_path, "-t", str(max_seconds), "-c", "copy", output_path],
        check=True, capture_output=True,
    )
    return output_path


def upload_for_wavespeed(local_path: str, progress_cb=None) -> str:
    """Upload to uguu.se — WaveSpeed can fetch from h.uguu.se (48h retention)."""
    fname = Path(local_path).name
    if progress_cb:
        progress_cb(f"Uploading {fname} for WaveSpeed...")
    with open(local_path, "rb") as f:
        r = requests.post(
            "https://uguu.se/upload",
            files={"files[]": (fname, f)},
            timeout=300,
        )
    r.raise_for_status()
    data = r.json()
    url = data["files"][0]["url"]
    if url.startswith("https://"):
        return url
    raise RuntimeError(f"Unexpected uguu response: {data}")


def download_url(url: str, dest_path: str) -> str:
    Path(dest_path).parent.mkdir(parents=True, exist_ok=True)
    with requests.get(url, stream=True, timeout=180) as r:
        r.raise_for_status()
        with open(dest_path, "wb") as f:
            for chunk in r.iter_content(chunk_size=65536):
                f.write(chunk)
    return dest_path

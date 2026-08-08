"""
audio_mixer.py — Trending audio selection and ffmpeg mixing.

Pulls from TikTok Creative Center top 50 automatically.
Returns (output_path, track_name) so the caller can display what was used.
"""

import subprocess
from pathlib import Path

from config import AUDIO_VOLUME, VIDEO_VOLUME
from trending_fetcher import get_random_trending
from downloader import download_audio


def add_trending_audio(reels_url: str) -> str:
    """Manually download a Reels/TikTok URL into trending_audio/ (from !audio command)."""
    from config import TRENDING_AUDIO_DIR
    d = Path(TRENDING_AUDIO_DIR)
    d.mkdir(parents=True, exist_ok=True)
    slug = reels_url.rstrip("/").split("/")[-1][:40].replace("?", "_")
    return download_audio(reels_url, str(d / slug))


def mix_audio(
    video_path: str,
    output_path: str,
    progress_cb=None,
) -> tuple[str, str]:
    """
    Overlay a trending sound on the video.

    Returns (output_path, track_label) where track_label is the song name.
    If no trending audio found, copies video unchanged and track_label = "no audio".
    """
    if progress_cb:
        progress_cb("Fetching trending audio...")

    track, audio_path = get_random_trending(top_n=20)

    if not track or not audio_path:
        if progress_cb:
            progress_cb("No trending audio available — skipping audio mix.")
        subprocess.run(
            ["ffmpeg", "-y", "-i", video_path, "-c", "copy", output_path],
            check=True, capture_output=True,
        )
        return output_path, "no audio"

    track_label = f"{track['title']} — {track['artist']}" if track.get("artist") else track["title"]
    if progress_cb:
        progress_cb(f"Audio: {track_label}")

    # Get video duration for audio trim
    probe = subprocess.run(
        ["ffprobe", "-v", "quiet",
         "-show_entries", "format=duration",
         "-of", "default=noprint_wrappers=1:nokey=1",
         video_path],
        capture_output=True, text=True,
    )
    try:
        duration = float(probe.stdout.strip())
    except ValueError:
        duration = 30.0

    cmd = [
        "ffmpeg", "-y",
        "-i", video_path,
        "-stream_loop", "-1", "-i", audio_path,
        "-filter_complex",
        (
            f"[0:a]volume={VIDEO_VOLUME}[va];"
            f"[1:a]volume={AUDIO_VOLUME},atrim=0:{duration},asetpts=PTS-STARTPTS[ta];"
            "[va][ta]amix=inputs=2:duration=first[aout]"
        ),
        "-map", "0:v",
        "-map", "[aout]",
        "-c:v", "copy",
        "-c:a", "aac",
        "-shortest",
        output_path,
    ]
    subprocess.run(cmd, check=True, capture_output=True)
    return output_path, track_label

"""
video_upscaler.py — Upscale video using ffmpeg Lanczos resampling.
Fast, free, no API cost. 2x is the sweet spot for quality vs file size.
"""

import subprocess
from pathlib import Path

FFMPEG = r"C:\Windows\ffmpeg.exe"


def upscale(input_path: str, output_path: str, scale: int = 2) -> str:
    """
    Upscale video by integer scale factor using Lanczos resampling.
    scale=2  →  1080p → 2160p (4K),  720p → 1440p, etc.
    Returns output_path on success, raises RuntimeError on failure.
    """
    cmd = [
        FFMPEG, "-y", "-i", input_path,
        "-vf", f"scale=iw*{scale}:ih*{scale}:flags=lanczos",
        "-c:v", "libx264", "-crf", "18", "-preset", "slow",
        "-c:a", "copy",
        output_path,
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"ffmpeg upscale error: {result.stderr[-400:]}")
    return output_path

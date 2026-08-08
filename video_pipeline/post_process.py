"""
post_process.py — Final ffmpeg encode + exiftool metadata strip.

After face swap and audio mix, this produces the clean uploadable file.
"""

import subprocess
from pathlib import Path

from config import VIDEO_CODEC, AUDIO_CODEC, CRF, OUTPUT_FORMAT


def encode_final(input_path: str, output_path: str, progress_cb=None) -> str:
    """
    Re-encode video for posting:
      - H.264 video, AAC audio
      - Strip all metadata streams
      - Fast-start (moov atom at front for streaming)
    """
    if progress_cb:
        progress_cb("Final encode (H.264 + AAC)...")

    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    cmd = [
        "ffmpeg", "-y",
        "-i", input_path,
        "-c:v", VIDEO_CODEC,
        "-crf", str(CRF),
        "-preset", "fast",
        "-c:a", AUDIO_CODEC,
        "-b:a", "192k",
        "-movflags", "+faststart",
        "-map_metadata", "-1",   # drop container metadata
        "-map_chapters", "-1",   # drop chapters
        output_path,
    ]
    subprocess.run(cmd, check=True, capture_output=True)
    return output_path


def strip_metadata(path: str, progress_cb=None) -> str:
    """
    Use exiftool to wipe all EXIF / XMP / IPTC / GPS metadata in-place.
    Silently skips if exiftool is not on PATH.
    Install: https://exiftool.org  (or: choco install exiftool)
    """
    import shutil
    if not shutil.which("exiftool"):
        if progress_cb:
            progress_cb("exiftool not found — metadata strip skipped (install from exiftool.org)")
        return path

    if progress_cb:
        progress_cb("Stripping metadata (exiftool)...")

    subprocess.run(
        ["exiftool", "-all=", "-overwrite_original", path],
        check=True, capture_output=True,
    )
    return path


def post_process(input_path: str, output_path: str, progress_cb=None) -> str:
    """Encode + strip metadata. Returns output_path."""
    encode_final(input_path, output_path, progress_cb)
    strip_metadata(output_path, progress_cb)
    return output_path

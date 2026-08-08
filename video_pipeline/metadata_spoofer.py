"""
metadata_spoofer.py — Inject realistic iPhone QuickTime metadata into video.

Uses ffmpeg to write Apple/iPhone device tags into the moov/udta atoms,
re-encodes to disrupt invisible AI watermarks, and strips original metadata.
"""

import subprocess
from datetime import datetime
from pathlib import Path

FFMPEG = r"C:\Windows\ffmpeg.exe"

IPHONE_MODELS = {
    "iPhone 16 Pro Max": "18.2",
    "iPhone 16 Pro":     "18.2",
    "iPhone 15 Pro Max": "17.6.1",
    "iPhone 15 Pro":     "17.6.1",
    "iPhone 15":         "17.6.1",
    "iPhone 14 Pro":     "16.7.2",
}
DEFAULT_MODEL = "iPhone 15 Pro"


def spoof(
    input_path: str,
    output_path: str,
    model: str = DEFAULT_MODEL,
    lat: float = 34.0522,
    lon: float = -118.2437,
    capture_time: datetime | None = None,
    disrupt_watermark: bool = True,
) -> str:
    """
    Write iPhone QuickTime metadata and optionally re-encode to disrupt watermarks.
    Returns output_path on success, raises RuntimeError on failure.
    """
    if capture_time is None:
        capture_time = datetime.now()

    software = IPHONE_MODELS.get(model, "17.6.1")
    ts       = capture_time.strftime("%Y-%m-%dT%H:%M:%S.000000Z")
    # ISO 6709 ±DD.DDDD±DDD.DDDD/ format
    iso6709  = f"{lat:+.4f}{lon:+.5f}/"

    cmd = [
        FFMPEG, "-y", "-i", input_path,
        # strip all incoming metadata first
        "-map_metadata", "-1",
        # QuickTime / iPhone tags
        "-metadata", "make=Apple",
        "-metadata", f"model={model}",
        "-metadata", f"software={software}",
        "-metadata", f"creation_time={ts}",
        "-metadata", f"location={iso6709}",
        "-metadata", f"location-eng={iso6709}",
        "-metadata", f"com.apple.quicktime.make=Apple",
        "-metadata", f"com.apple.quicktime.model={model}",
        "-metadata", f"com.apple.quicktime.software={software}",
        "-metadata", f"com.apple.quicktime.creationdate={ts}",
        "-metadata", f"com.apple.quicktime.location.ISO6709={iso6709}",
        # mov flags — write QuickTime-style tags, fast-start for web
        "-movflags", "use_metadata_tags+faststart",
    ]

    if disrupt_watermark:
        # Re-encode with subtle noise to disrupt DCT/LSB invisible watermarks
        cmd += [
            "-c:v", "libx264",
            "-crf", "20",
            "-preset", "fast",
            "-profile:v", "high",
            "-pix_fmt", "yuv420p",
            "-vf", "noise=alls=2:allf=t+u",
            "-c:a", "aac", "-b:a", "128k",
        ]
    else:
        cmd += ["-c", "copy"]

    cmd.append(output_path)

    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"ffmpeg error: {result.stderr[-400:]}")

    return output_path

"""
frame_extractor.py — Extract the frame with the clearest face+body from a video.

Priority: face visible > sharpness. Tries frontal and profile Haar cascades.
Falls back to skin-tone detection if no face found. Samples 24 candidates.
"""

import os
import shutil
import subprocess
import tempfile
import urllib.request
from pathlib import Path

_HERE = Path(__file__).parent
_CASCADE_FRONT   = str(_HERE / "haarcascade_frontalface_default.xml")
_CASCADE_PROFILE = str(_HERE / "haarcascade_profileface.xml")

_CASCADE_URLS = {
    _CASCADE_FRONT:   "https://raw.githubusercontent.com/opencv/opencv/master/data/haarcascades/haarcascade_frontalface_default.xml",
    _CASCADE_PROFILE: "https://raw.githubusercontent.com/opencv/opencv/master/data/haarcascades/haarcascade_profileface.xml",
}


def _ensure_cascades():
    for path, url in _CASCADE_URLS.items():
        if not Path(path).exists():
            try:
                urllib.request.urlretrieve(url, path)
            except Exception as e:
                print(f"[frame_extractor] Could not download cascade {path}: {e}")


def _get_duration(video_path: str) -> float:
    import re
    result = subprocess.run(["ffmpeg", "-i", video_path], capture_output=True, text=True)
    m = re.search(r"Duration:\s*(\d+):(\d+):([\d.]+)", result.stderr)
    if m:
        h, mn, s = int(m.group(1)), int(m.group(2)), float(m.group(3))
        return h * 3600 + mn * 60 + s
    return 10.0


def _score_frame(img_path: str) -> float:
    """Score a frame: face-detected frames score much higher than faceless ones."""
    try:
        import cv2
        import numpy as np

        img = cv2.imread(img_path)
        if img is None:
            return 0.0

        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        h, w = gray.shape
        sharpness = float(cv2.Laplacian(gray, cv2.CV_64F).var())

        # Try both frontal and profile cascades at multiple scales
        best_face_area = 0
        face_center_y  = 0.5
        for cascade_path in (_CASCADE_FRONT, _CASCADE_PROFILE):
            if not Path(cascade_path).exists():
                continue
            cc = cv2.CascadeClassifier(cascade_path)
            if cc.empty():
                continue
            for scale in (1.05, 1.1, 1.2):
                faces = cc.detectMultiScale(
                    gray, scaleFactor=scale, minNeighbors=3, minSize=(20, 20)
                )
                if len(faces) > 0:
                    for fx, fy, fw, fh in faces:
                        area = fw * fh
                        if area > best_face_area:
                            best_face_area = area
                            face_center_y  = (fy + fh / 2) / h

        if best_face_area > 0:
            face_ratio = best_face_area / (w * h)
            # Bonus when face is in top half (body visible below)
            position_bonus = 1.5 if face_center_y < 0.5 else 1.0
            return sharpness * (1 + face_ratio * 20) * position_bonus

        # No face detected — use skin-tone proxy (top third of frame)
        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        skin_mask = cv2.inRange(hsv, np.array([0, 20, 70], dtype=np.uint8),
                                     np.array([25, 255, 255], dtype=np.uint8))
        skin_ratio = float(np.sum(skin_mask[:h // 3, :] > 0)) / max(w * h // 3, 1)
        # Penalise frames with no face heavily
        return sharpness * skin_ratio * 0.1

    except Exception:
        try:
            from PIL import Image, ImageFilter
            import numpy as np
            img = Image.open(img_path).convert("L")
            return float(np.array(img.filter(ImageFilter.FIND_EDGES), dtype=float).var())
        except Exception:
            try:
                return float(os.path.getsize(img_path))
            except Exception:
                return 0.0


def extract_best_frame(video_path: str, output_path: str, n_candidates: int = 24) -> str:
    """
    Extract the frame with the clearest face+body.
    Returns output_path on success, raises RuntimeError on failure.
    """
    _ensure_cascades()

    duration = _get_duration(video_path)
    margin   = duration * 0.05
    usable   = duration - 2 * margin

    if n_candidates < 2:
        n_candidates = 2
    timestamps = [
        margin + usable * i / (n_candidates - 1)
        for i in range(n_candidates)
    ]

    best_score = -1.0
    best_src   = None

    with tempfile.TemporaryDirectory() as tmp:
        for i, ts in enumerate(timestamps):
            frame_path = os.path.join(tmp, f"frame_{i:03d}.jpg")
            subprocess.run(
                ["ffmpeg", "-y", "-ss", f"{ts:.3f}", "-i", video_path,
                 "-frames:v", "1", "-q:v", "2", frame_path],
                capture_output=True,
            )
            if not os.path.exists(frame_path):
                continue
            score = _score_frame(frame_path)
            if score > best_score:
                best_score = score
                best_src   = frame_path

        if not best_src:
            raise RuntimeError("No frames could be extracted from the video")

        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(best_src, output_path)

    return output_path

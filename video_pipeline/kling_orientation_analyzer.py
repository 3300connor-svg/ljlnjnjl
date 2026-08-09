"""
kling_orientation_analyzer.py — Recommend Kling character_orientation for a video.

"image"  → derive orientation from the reference image (front-facing swap).
           No hard output cap. Best when subject faces the camera.
"video"  → derive orientation from the driving video's pose path.
           Kling hard-caps output at 10s in this mode. Best for tracking
           shots, angled subjects, or heavy camera movement.

Decision signals (in priority order):
  1. Duration > 10s         → image  (video mode would clip the output at 10s)
  2. High camera motion     → video  (tracking/handheld shots need video alignment)
  3. Profile/angled dominant → video  (subject pose differs from front-facing swap)
  4. Frontal face dominant  → image  (pose matches the swap image)
  5. Moderate motion, no clear face → video  (motion > static safe default)
  6. Fallback               → image  (front-facing is the common Instagram case)
"""

import os
import re
import subprocess
import tempfile
from pathlib import Path

_CASCADE_FRONT   = str(Path(__file__).parent / "haarcascade_frontalface_default.xml")
_CASCADE_PROFILE = str(Path(__file__).parent / "haarcascade_profileface.xml")

# Mean inter-frame pixel delta thresholds (0–255 scale, measured on 160×90 grey)
_MOTION_HIGH = 18.0   # above → significant camera movement → video
_MOTION_MID  = 8.0    # above → moderate movement (used as tiebreaker)

_FRONTAL_MIN = 0.45   # fraction of frames needing a frontal hit to call it front-facing
_PROFILE_MIN = 0.30   # fraction of profile-only frames to call it angled

_N_SAMPLES = 8        # frames sampled for analysis


def _get_duration(video_path: str) -> float:
    result = subprocess.run(["ffmpeg", "-i", video_path], capture_output=True, text=True)
    m = re.search(r"Duration:\s*(\d+):(\d+):([\d.]+)", result.stderr)
    if m:
        h, mn, s = int(m.group(1)), int(m.group(2)), float(m.group(3))
        return h * 3600 + mn * 60 + s
    return 10.0


def _sample_frames(video_path: str, duration: float, n: int) -> list:
    """Return n evenly-spaced BGR frames as a list of numpy arrays."""
    try:
        import cv2
    except ImportError:
        return []

    margin = duration * 0.05
    usable = max(duration - 2 * margin, duration * 0.5)
    frames = []

    with tempfile.TemporaryDirectory() as tmp:
        for i in range(n):
            ts = margin + usable * i / max(n - 1, 1)
            p  = os.path.join(tmp, f"f{i:03d}.jpg")
            subprocess.run(
                ["ffmpeg", "-y", "-ss", f"{ts:.3f}", "-i", video_path,
                 "-frames:v", "1", "-q:v", "3", p],
                capture_output=True,
            )
            if os.path.exists(p):
                img = cv2.imread(p)
                if img is not None:
                    frames.append(img)

    return frames


def analyze_orientation(video_path: str) -> dict:
    """
    Analyze video and return orientation recommendation for Kling.

    Return value:
      {
        "recommendation": "image" | "video",
        "reasons": [str, ...],        # plain-language explanations, first is shown in UI
        "signals": {
          "duration_s":          float,
          "frontal_face_ratio":  float,  # fraction of sampled frames with frontal face
          "profile_only_ratio":  float,  # fraction with profile hit but no frontal
          "mean_motion":         float,  # mean inter-frame pixel delta
          "mean_face_area_ratio": float, # mean face-area / frame-area
        }
      }
    """
    reasons: list[str] = []
    signals = {
        "duration_s":           0.0,
        "frontal_face_ratio":   0.0,
        "profile_only_ratio":   0.0,
        "mean_motion":          0.0,
        "mean_face_area_ratio": 0.0,
    }

    def _ret(rec: str) -> dict:
        return {"recommendation": rec, "reasons": reasons, "signals": signals}

    # ── 1. Duration ───────────────────────────────────────────────────────────
    duration = _get_duration(video_path)
    signals["duration_s"] = round(duration, 2)

    if duration > 10.0:
        reasons.append(
            f"video is {duration:.1f}s — video mode hard-caps Kling output at 10s, "
            "image mode has no cap"
        )
        return _ret("image")

    # ── 2. Sample frames ──────────────────────────────────────────────────────
    frames = _sample_frames(video_path, duration, _N_SAMPLES)

    if not frames:
        reasons.append("could not sample frames — defaulting to image (safe front-facing default)")
        return _ret("image")

    try:
        import cv2
        import numpy as np

        front_cc   = cv2.CascadeClassifier(_CASCADE_FRONT)   if Path(_CASCADE_FRONT).exists()   else None
        profile_cc = cv2.CascadeClassifier(_CASCADE_PROFILE) if Path(_CASCADE_PROFILE).exists() else None

        n_frontal      = 0
        n_profile_only = 0
        face_areas: list[float] = []

        for img in frames:
            h, w    = img.shape[:2]
            gray    = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            frontal = False
            profile = False
            best_area = 0

            if front_cc and not front_cc.empty():
                hits = front_cc.detectMultiScale(
                    gray, scaleFactor=1.1, minNeighbors=3, minSize=(20, 20)
                )
                if len(hits) > 0:
                    frontal = True
                    for (fx, fy, fw, fh) in hits:
                        best_area = max(best_area, fw * fh)

            if profile_cc and not profile_cc.empty():
                hits = profile_cc.detectMultiScale(
                    gray, scaleFactor=1.1, minNeighbors=3, minSize=(20, 20)
                )
                if len(hits) > 0:
                    if not frontal:
                        profile = True
                    for (fx, fy, fw, fh) in hits:
                        best_area = max(best_area, fw * fh)

            if frontal:
                n_frontal += 1
            elif profile:
                n_profile_only += 1

            if best_area > 0:
                face_areas.append(best_area / (w * h))

        n = len(frames)
        frontal_ratio  = n_frontal / n
        profile_ratio  = n_profile_only / n
        mean_face_area = float(np.mean(face_areas)) if face_areas else 0.0

        signals["frontal_face_ratio"]   = round(frontal_ratio, 3)
        signals["profile_only_ratio"]   = round(profile_ratio, 3)
        signals["mean_face_area_ratio"] = round(mean_face_area, 4)

        # ── Inter-frame motion (optical-flow proxy) ───────────────────────────
        deltas: list[float] = []
        for i in range(1, len(frames)):
            a = cv2.cvtColor(cv2.resize(frames[i - 1], (160, 90)), cv2.COLOR_BGR2GRAY)
            b = cv2.cvtColor(cv2.resize(frames[i],     (160, 90)), cv2.COLOR_BGR2GRAY)
            deltas.append(float(cv2.absdiff(a, b).mean()))

        mean_motion = float(np.mean(deltas)) if deltas else 0.0
        signals["mean_motion"] = round(mean_motion, 2)

    except Exception as e:
        reasons.append(f"frame analysis error ({e}) — defaulting to image")
        return _ret("image")

    # ── Decision tree ─────────────────────────────────────────────────────────

    # Signal 2: Heavy camera movement → video orientation tracks the shot
    if mean_motion > _MOTION_HIGH:
        reasons.append(
            f"high camera movement (inter-frame delta {mean_motion:.1f}, threshold {_MOTION_HIGH}) "
            "— video orientation follows the shot"
        )
        if profile_ratio > frontal_ratio:
            reasons.append(
                f"subject also angled/profile in {profile_ratio*100:.0f}% of frames"
            )
        return _ret("video")

    # Signal 3: Profile-dominant without heavy motion → angled subject
    if profile_ratio >= _PROFILE_MIN and profile_ratio > frontal_ratio:
        reasons.append(
            f"subject appears angled or profile in {profile_ratio*100:.0f}% of frames "
            f"vs front-facing in {frontal_ratio*100:.0f}% "
            "— video orientation matches the pose"
        )
        return _ret("video")

    # Signal 4: Clear frontal dominance → image orientation
    if frontal_ratio >= _FRONTAL_MIN:
        motion_note = (
            f", low camera movement (delta {mean_motion:.1f})"
            if mean_motion < _MOTION_MID else ""
        )
        reasons.append(
            f"face is front-facing in {frontal_ratio*100:.0f}% of frames{motion_note} "
            "— image orientation matches the swap image pose"
        )
        return _ret("image")

    # Signal 5: Moderate motion, no clear face signal
    if mean_motion > _MOTION_MID:
        reasons.append(
            f"moderate camera movement (delta {mean_motion:.1f}) with no clear face orientation "
            "— video mode adapts better to movement"
        )
        return _ret("video")

    # Signal 6: Fallback
    reasons.append(
        f"low motion (delta {mean_motion:.1f}), no strong pose signal "
        "— defaulting to image (safe choice for front-facing Instagram content)"
    )
    return _ret("image")

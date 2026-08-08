"""
kling_motion_client.py — Kling 3.0 Std Motion Control client.

Model: kwaivgi/kling-v3.0-std/motion-control
Pricing: $0.378 (≤3s) / $0.63 (5s) / $1.26 (10s) / $3.78 (30s max)

Takes a character image + driving video, transfers the motion.
character_orientation="video" supports up to 30s.
"""

import time
import random
import requests
from pathlib import Path

from config import WAVESPEED_BASE

STD_MODEL = "kwaivgi/kling-v3.0-std/motion-control"
PRO_MODEL = "kwaivgi/kling-v3.0-pro/motion-control"
POLL_INTERVAL = 10
MAX_POLL_SECS = 600


class KlingMotionClient:
    def __init__(self, api_key: str, model: str = STD_MODEL):
        self.model = model
        self.base  = WAVESPEED_BASE.rstrip("/") + "/api/v3"
        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        })

    def motion_control(
        self,
        image_url: str,
        video_url: str,
        output_path: str,
        orientation: str = "video",
        keep_sound: bool = True,
        prompt: str = "",
        progress_cb=None,
    ) -> str:
        if progress_cb:
            progress_cb("Submitting to Kling 3.0 Motion Control...")

        body = {
            "image": image_url,
            "video": video_url,
            "character_orientation": orientation,
            "keep_original_sound": keep_sound,
        }
        if prompt:
            body["prompt"] = prompt

        r = self.session.post(f"{self.base}/{self.model}", json=body, timeout=30)
        if r.status_code >= 400:
            try:
                msg = r.json().get("message", r.text[:200])
            except Exception:
                msg = r.text[:200]
            raise RuntimeError(f"Kling API {r.status_code}: {msg}")

        task_id = r.json()["data"]["id"]
        if progress_cb:
            progress_cb(f"Processing (task {task_id[:8]}...)  polling every {POLL_INTERVAL}s")

        deadline = time.time() + MAX_POLL_SECS
        while time.time() < deadline:
            r = self.session.get(
                f"{self.base}/predictions/{task_id}/result", timeout=30
            )
            data = r.json().get("data", {})
            status = data.get("status")
            if status == "completed":
                outputs = data.get("outputs", [])
                if not outputs:
                    raise RuntimeError("Kling completed but returned no output")
                out_url = outputs[0]
                if progress_cb:
                    progress_cb("Downloading output video...")
                Path(output_path).parent.mkdir(parents=True, exist_ok=True)
                with requests.get(out_url, stream=True, timeout=300) as dl:
                    dl.raise_for_status()
                    with open(output_path, "wb") as f:
                        for chunk in dl.iter_content(65536):
                            f.write(chunk)
                size_kb = Path(output_path).stat().st_size // 1024
                if progress_cb:
                    progress_cb(f"Done ({size_kb} KB)")
                return output_path
            if status == "failed":
                raise RuntimeError(f"Kling failed: {data.get('error', 'unknown error')}")
            time.sleep(POLL_INTERVAL + random.uniform(0, 2))

        raise RuntimeError(f"Kling timed out after {MAX_POLL_SECS}s on task {task_id}")

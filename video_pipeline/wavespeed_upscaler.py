"""
wavespeed_upscaler.py — Image upscaling via wavespeed-ai/real-esrgan.

Upscales the swap image before it's passed to Kling, giving Kling a higher
quality input and producing sharper, more detailed final video.
"""

import time
import requests
from pathlib import Path

from config import WAVESPEED_API_KEY, WAVESPEED_BASE

MODEL        = "wavespeed-ai/real-esrgan"
POLL_INTERVAL = 3
MAX_POLL_SECS = 120


class WaveSpeedUpscaler:
    def __init__(self, api_key: str = WAVESPEED_API_KEY):
        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        })
        self.base = WAVESPEED_BASE.rstrip("/") + "/api/v3"

    def upscale(self, image_url: str, output_path: str, progress_cb=None) -> str:
        """
        Upscale image_url with Real-ESRGAN, download result to output_path.
        Returns output_path on success.
        """
        if progress_cb:
            progress_cb("Submitting to WaveSpeed upscaler...")

        last_err = None
        for attempt in range(3):
            try:
                r = self.session.post(
                    f"{self.base}/{MODEL}",
                    json={"image": image_url},
                    timeout=30,
                )
                break
            except Exception as e:
                last_err = e
                if attempt < 2:
                    time.sleep(5)
        else:
            raise RuntimeError(f"Upscaler connection failed after 3 attempts: {last_err}")

        if r.status_code >= 400:
            try:
                msg = r.json().get("message", r.text[:200])
            except Exception:
                msg = r.text[:200]
            raise RuntimeError(f"Upscaler API {r.status_code}: {msg}")

        task_id = r.json()["data"]["id"]

        if progress_cb:
            progress_cb(f"Upscaling (task {task_id[:8]}...)...")

        deadline = time.time() + MAX_POLL_SECS
        while time.time() < deadline:
            poll = self.session.get(
                f"{self.base}/predictions/{task_id}/result",
                timeout=20,
            ).json().get("data", {})
            status = poll.get("status")
            if status == "completed":
                outputs = poll.get("outputs", [])
                if not outputs:
                    raise RuntimeError("Upscaler returned no output")
                image_url_out = outputs[0]
                break
            if status == "failed":
                raise RuntimeError(f"Upscaler failed: {poll.get('error', 'unknown')}")
            time.sleep(POLL_INTERVAL)
        else:
            raise RuntimeError(f"Upscaler timed out after {MAX_POLL_SECS}s")

        if progress_cb:
            progress_cb("Downloading upscaled image...")

        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        with requests.get(image_url_out, stream=True, timeout=60) as dl:
            dl.raise_for_status()
            with open(output_path, "wb") as f:
                for chunk in dl.iter_content(65536):
                    f.write(chunk)

        return output_path

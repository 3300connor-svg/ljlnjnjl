"""
wavespeed_video.py — WaveSpeed WAN 2.2 face swap client.

Submits a face swap job, polls until done, downloads the result.
The source video must be a publicly accessible URL (use downloader.upload_temp).
"""

import time
import random
import requests
from pathlib import Path

from config import WAVESPEED_BASE, FACE_REFERENCE_URL, WAN_MODEL, FACE_SWAP_PROMPT

POLL_INTERVAL   = 10     # seconds between status checks
MAX_POLL_SECS   = 600    # 10 min max per video
REQUEST_TIMEOUT = 30


class WaveSpeedVideoError(Exception):
    def __init__(self, code: str, message: str, status: int = 0):
        self.code    = code
        self.message = message
        self.status  = status
        super().__init__(f"[{status} {code}] {message}")


class WaveSpeedVideoClient:
    def __init__(self, api_key: str):
        self.base = WAVESPEED_BASE.rstrip("/") + "/api/v3"
        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"Bearer {api_key}",
            "Content-Type":  "application/json",
        })

    def get_balance(self) -> float:
        r = self.session.get(f"{self.base}/balance", timeout=REQUEST_TIMEOUT)
        return float(r.json().get("data", {}).get("balance", 0))

    def _submit(self, source_video_url: str) -> str:
        """Submit face swap job and return task ID."""
        body = {
            "video":         source_video_url,
            "face_image":    FACE_REFERENCE_URL,
            "target_gender": "female",
            "target_index":  0,
        }
        r = self.session.post(f"{self.base}/{WAN_MODEL}", json=body, timeout=REQUEST_TIMEOUT)
        if r.status_code >= 400:
            try:
                msg = r.json().get("message", r.text[:200])
            except Exception:
                msg = r.text[:200]
            raise WaveSpeedVideoError("api_error", msg, r.status_code)
        return r.json()["data"]["id"]

    def _poll(self, task_id: str) -> str:
        """Poll until completed, return output video URL."""
        deadline = time.time() + MAX_POLL_SECS
        while time.time() < deadline:
            r = self.session.get(
                f"{self.base}/predictions/{task_id}/result",
                timeout=REQUEST_TIMEOUT,
            )
            data   = r.json().get("data", {})
            status = data.get("status")
            if status == "completed":
                outputs = data.get("outputs", [])
                if not outputs:
                    raise WaveSpeedVideoError("no_output", "Completed but empty output list")
                return outputs[0]
            if status == "failed":
                raise WaveSpeedVideoError("generation_failed", data.get("error", "unknown error"))
            time.sleep(POLL_INTERVAL + random.uniform(0, 3))
        raise WaveSpeedVideoError("timeout", f"Timed out after {MAX_POLL_SECS}s on task {task_id}")

    def video_edit(
        self,
        source_video_url: str,
        prompt: str,
        output_path: str,
        resolution: str = "480p",
        progress_cb=None,
    ) -> str:
        """
        Edit a video with a text prompt (clothing, style, scene changes).
        Model: wavespeed-ai/wan-2.2/video-edit — $0.20/video
        """
        if progress_cb:
            progress_cb(f"Clothes swap: {prompt[:60]}...")
        body = {
            "video":      source_video_url,
            "prompt":     prompt,
            "resolution": resolution,
            "seed":       -1,
        }
        r = self.session.post(
            f"{self.base}/wavespeed-ai/wan-2.2/video-edit",
            json=body, timeout=REQUEST_TIMEOUT,
        )
        if r.status_code >= 400:
            raise WaveSpeedVideoError("api_error", r.text[:200], r.status_code)
        task_id    = r.json()["data"]["id"]
        output_url = self._poll(task_id)
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        with requests.get(output_url, stream=True, timeout=180) as dl:
            dl.raise_for_status()
            with open(output_path, "wb") as f:
                for chunk in dl.iter_content(65536):
                    f.write(chunk)
        return output_path

    def face_swap(
        self,
        source_video_url: str,
        output_path: str,
        progress_cb=None,
    ) -> str:
        """
        Full face swap: submit → poll → download result.

        source_video_url : publicly accessible URL of the source video
        output_path      : local path to save the swapped video
        progress_cb      : optional callable(msg: str) for status updates
        Returns          : output_path
        """
        if progress_cb:
            progress_cb("Submitting to WaveSpeed WAN 2.2...")
        task_id = self._submit(source_video_url)
        if progress_cb:
            progress_cb(f"Processing (task {task_id[:8]}...)  polling every {POLL_INTERVAL}s")
        output_url = self._poll(task_id)
        if progress_cb:
            progress_cb("Downloading face-swapped video...")
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        with requests.get(output_url, stream=True, timeout=180) as dl:
            dl.raise_for_status()
            with open(output_path, "wb") as f:
                for chunk in dl.iter_content(65536):
                    f.write(chunk)
        return output_path

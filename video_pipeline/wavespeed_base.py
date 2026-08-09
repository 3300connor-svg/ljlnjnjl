"""
wavespeed_base.py — Shared submit/poll/download client for WaveSpeed API jobs.

kling_motion_client, wavespeed_upscaler, and seedream_client's fallback path
all hit the same WaveSpeed submit -> poll -> download pattern. This keeps
retry, timeout, and error handling consistent across them instead of each
reimplementing it slightly differently.
"""

import time
import random
import requests
from pathlib import Path

from config import WAVESPEED_BASE


class WaveSpeedError(RuntimeError):
    pass


class WaveSpeedJobClient:
    def __init__(self, api_key: str, poll_interval: float = 5, max_poll_secs: float = 300):
        self.base          = WAVESPEED_BASE.rstrip("/") + "/api/v3"
        self.poll_interval = poll_interval
        self.max_poll_secs = max_poll_secs
        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"Bearer {api_key}",
            "Content-Type":  "application/json",
        })

    def submit(self, model: str, body: dict, retries: int = 3, retry_wait: float = 5) -> str:
        """POST a job, return its task id. Retries on connection errors, not on 4xx/5xx."""
        last_err = None
        for attempt in range(retries):
            try:
                r = self.session.post(f"{self.base}/{model}", json=body, timeout=30)
            except requests.RequestException as e:
                last_err = e
                if attempt < retries - 1:
                    time.sleep(retry_wait)
                continue
            if r.status_code >= 400:
                try:
                    msg = r.json().get("message", r.text[:200])
                except Exception:
                    msg = r.text[:200]
                raise WaveSpeedError(f"{model} API {r.status_code}: {msg}")
            return r.json()["data"]["id"]
        raise WaveSpeedError(f"{model} connection failed after {retries} attempts: {last_err}")

    def poll(self, task_id: str, model: str = "job") -> str:
        """Poll until completed, return the first output URL."""
        deadline = time.time() + self.max_poll_secs
        while time.time() < deadline:
            r = self.session.get(f"{self.base}/predictions/{task_id}/result", timeout=30)
            if r.status_code >= 400:
                try:
                    msg = r.json().get("message", r.text[:200])
                except Exception:
                    msg = r.text[:200]
                raise WaveSpeedError(f"{model} poll {r.status_code}: {msg}")
            data   = r.json().get("data", {})
            status = data.get("status")
            if status == "completed":
                outputs = data.get("outputs", [])
                if not outputs:
                    raise WaveSpeedError(f"{model} completed but returned no output")
                return outputs[0]
            if status == "failed":
                raise WaveSpeedError(f"{model} failed: {data.get('error', 'unknown error')}")
            time.sleep(self.poll_interval + random.uniform(0, self.poll_interval * 0.3))
        raise WaveSpeedError(f"{model} timed out after {self.max_poll_secs}s on task {task_id}")

    def download(self, url: str, output_path: str, timeout: float = 180) -> str:
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        with requests.get(url, stream=True, timeout=timeout) as dl:
            dl.raise_for_status()
            with open(output_path, "wb") as f:
                for chunk in dl.iter_content(65536):
                    f.write(chunk)
        return output_path

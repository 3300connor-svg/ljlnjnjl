"""
seedream_client.py — Seedream 4.5 Edit image generation via WaveSpeedClient.

Uses the robust WaveSpeedClient from the parent package (retry, backoff,
rate-limit handling). Supports multiple reference images: scene + face + body.
Model: bytedance/seedream-v4.5/edit  ($0.04/image)
"""

import sys
import time
import requests
from pathlib import Path

# Pull in the battle-tested client from the parent package
sys.path.insert(0, str(Path(__file__).parent.parent / "wavespeed-batch-api"))
try:
    from wavespeed_client import WaveSpeedClient, WaveSpeedError
except ImportError:
    WaveSpeedClient = None
    WaveSpeedError  = Exception

from config import WAVESPEED_API_KEY, WAVESPEED_BASE

MODEL        = "bytedance/seedream-v4.5/edit"
SIZE_9_16_2K = "1440*2560"
POLL_INTERVAL   = 5
MAX_POLL_SECS   = 300


def _ensure_catbox_url(url: str) -> str:
    """
    If url is not already on a WaveSpeed-friendly host (catbox/files.catbox),
    re-upload it to Catbox and return the new URL.
    """
    if not url:
        return url
    friendly_hosts = ("files.catbox.moe", "catbox.moe", "cdn.wavespeed")
    if any(h in url for h in friendly_hosts):
        return url
    # Re-upload to Catbox
    import mimetypes
    try:
        r = requests.get(url, timeout=30, headers={"User-Agent": "Mozilla/5.0"})
        r.raise_for_status()
        fname = url.split("/")[-1].split("?")[0] or "image.jpg"
        mime  = r.headers.get("content-type", "image/jpeg").split(";")[0]
        upload = requests.post(
            "https://catbox.moe/user/api.php",
            data={"reqtype": "fileupload", "userhash": ""},
            files={"fileToUpload": (fname, r.content, mime)},
            timeout=120,
        )
        upload.raise_for_status()
        catbox_url = upload.text.strip()
        if catbox_url.startswith("https://"):
            print(f"[seedream] mirrored {url[:50]}... → {catbox_url}")
            return catbox_url
    except Exception as e:
        print(f"[seedream] mirror to catbox failed: {e}, using original URL")
    return url


class SeedreamClient:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base    = WAVESPEED_BASE.rstrip("/") + "/api/v3"
        if WaveSpeedClient is not None:
            self._ws = WaveSpeedClient(api_key, base_url=WAVESPEED_BASE)
        else:
            self._ws = None
        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        })

    def _post(self, body: dict) -> str:
        """Submit job, return task_id. Retries up to 3x on connection errors."""
        last_err = None
        for attempt in range(3):
            try:
                if self._ws is not None:
                    resp = self._ws._request("POST", MODEL, json=body)
                else:
                    resp = self.session.post(f"{self.base}/{MODEL}", json=body, timeout=30)
                    if resp.status_code >= 400:
                        try:
                            msg = resp.json().get("message", resp.text[:200])
                        except Exception:
                            msg = resp.text[:200]
                        raise RuntimeError(f"Seedream API {resp.status_code}: {msg}")
                return resp.json()["data"]["id"]
            except RuntimeError:
                raise
            except Exception as e:
                last_err = e
                if attempt < 2:
                    time.sleep(5)
        raise RuntimeError(f"Seedream connection failed after 3 attempts: {last_err}")

    def _poll(self, task_id: str, progress_cb=None) -> str:
        """Poll until completed, return output image URL."""
        if self._ws is not None:
            return self._ws._poll(task_id, timeout=MAX_POLL_SECS)
        # Fallback polling
        deadline = time.time() + MAX_POLL_SECS
        while time.time() < deadline:
            r = self.session.get(
                f"{self.base}/predictions/{task_id}/result", timeout=30
            )
            data   = r.json().get("data", {})
            status = data.get("status")
            if status == "completed":
                outputs = data.get("outputs", [])
                if not outputs:
                    raise RuntimeError("Seedream completed but returned no output")
                return outputs[0]
            if status == "failed":
                raise RuntimeError(f"Seedream failed: {data.get('error', 'unknown')}")
            time.sleep(POLL_INTERVAL)
        raise RuntimeError(f"Seedream timed out after {MAX_POLL_SECS}s on task {task_id}")

    def generate(
        self,
        prompt: str,
        face_url: str,
        output_path: str,
        body_url: str   = "",
        scene_url: str  = "",
        size: str       = SIZE_9_16_2K,
        progress_cb=None,
    ) -> str:
        # URLs are pre-validated by bot.py (uguu.se or ibb.co — both WaveSpeed-accessible)
        if progress_cb:
            progress_cb("Submitting to WaveSpeed API...")

        # scene first so model treats it as the base scene
        images = []
        if scene_url:
            images.append(scene_url)
        images.append(face_url)
        if body_url:
            images.append(body_url)

        body = {
            "images": images,
            "prompt": prompt,
            "size": size,
            "enable_sync_mode": False,
            "enable_base64_output": False,
        }

        task_id = self._post(body)
        if progress_cb:
            progress_cb(f"Processing (task {task_id[:8]}...)...")

        image_url = self._poll(task_id, progress_cb=progress_cb)

        if progress_cb:
            progress_cb("Downloading result image...")
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        with requests.get(image_url, stream=True, timeout=60) as dl:
            dl.raise_for_status()
            with open(output_path, "wb") as f:
                for chunk in dl.iter_content(65536):
                    f.write(chunk)
        return output_path

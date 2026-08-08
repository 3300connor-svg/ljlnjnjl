"""
wavespeed_client.py — WaveSpeed Batch API client
Model: bytedance/seedream-v4.5/edit (image-to-image)
Pricing: $0.04/image flat

Usage:
    from wavespeed_client import WaveSpeedClient
    client = WaveSpeedClient(api_key="YOUR_KEY")
    print(client.get_balance())
    result = client.batch_generate(jobs=[...], avatar_url="...", output_dir="outputs/name_b1")
"""

import json
import os
import random
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from pathlib import Path
from typing import Callable, Optional, Tuple

import requests

BASE_URL = "https://api.wavespeed.ai"
API_PREFIX = "/api/v3"
IMAGE_MODEL = "bytedance/seedream-v4.5/edit"
REQUEST_TIMEOUT = 30
POLL_INTERVAL = 5
MAX_POLL_TIMEOUT = 300
MAX_BACKOFF_RETRIES = 5


class WaveSpeedError(Exception):
    def __init__(self, code: str, message: str, status: int = 0):
        self.code = code
        self.message = message
        self.status = status
        super().__init__(f"[{status} {code}] {message}")


def _lock_file(fd):
    if sys.platform == "win32":
        import msvcrt
        msvcrt.locking(fd.fileno(), msvcrt.LK_NBLCK, 1)
    else:
        import fcntl
        fcntl.flock(fd.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)


def _unlock_file(fd):
    if sys.platform == "win32":
        import msvcrt
        try:
            msvcrt.locking(fd.fileno(), msvcrt.LK_UNLCK, 1)
        except Exception:
            pass
    else:
        import fcntl
        try:
            fcntl.flock(fd.fileno(), fcntl.LOCK_UN)
        except Exception:
            pass


class WaveSpeedClient:
    def __init__(self, api_key: str, base_url: str = BASE_URL):
        if not api_key:
            raise ValueError("API key required.")
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        })

    def _url(self, path: str) -> str:
        return f"{self.base_url}{API_PREFIX}/{path}"

    def _request(self, method: str, path: str, **kwargs) -> requests.Response:
        url = self._url(path)
        delay = 1.0
        resp = None
        for attempt in range(MAX_BACKOFF_RETRIES):
            try:
                resp = self.session.request(method, url, timeout=REQUEST_TIMEOUT, **kwargs)
            except requests.exceptions.RequestException as e:
                if attempt == MAX_BACKOFF_RETRIES - 1:
                    raise WaveSpeedError("network_error", str(e))
                time.sleep(delay + random.uniform(0, 0.5))
                delay *= 2
                continue

            if resp.status_code == 429:
                retry_after = float(resp.headers.get("Retry-After", "0"))
                wait = max(retry_after, delay) + random.uniform(0, 0.3)
                if attempt == MAX_BACKOFF_RETRIES - 1:
                    self._raise_from_response(resp)
                time.sleep(wait)
                delay *= 2
                continue

            if 500 <= resp.status_code < 600:
                if attempt == MAX_BACKOFF_RETRIES - 1:
                    self._raise_from_response(resp)
                time.sleep(delay + random.uniform(0, 0.5))
                delay *= 2
                continue

            if 400 <= resp.status_code < 500:
                self._raise_from_response(resp)

            return resp

        self._raise_from_response(resp)

    def _raise_from_response(self, resp: requests.Response):
        try:
            data = resp.json()
            raise WaveSpeedError(
                code=data.get("message", "unknown"),
                message=data.get("message", resp.text[:200]),
                status=resp.status_code,
            )
        except (ValueError, KeyError):
            raise WaveSpeedError("http_error", resp.text[:200], resp.status_code)

    def _poll(self, task_id: str, timeout: int = MAX_POLL_TIMEOUT) -> str:
        deadline = time.time() + timeout
        while time.time() < deadline:
            resp = self._request("GET", f"predictions/{task_id}/result")
            data = resp.json().get("data", {})
            status = data.get("status")
            if status == "completed":
                outputs = data.get("outputs", [])
                if not outputs:
                    raise WaveSpeedError("generation_failed", "Completed but no output URL.")
                return outputs[0]
            if status == "failed":
                raise WaveSpeedError("generation_failed", data.get("error", "Generation failed"))
            time.sleep(POLL_INTERVAL + random.uniform(0, 1.0))
        raise WaveSpeedError("polling_timeout", f"Timeout after {timeout}s on task {task_id}")

    def _download(self, url: str, dest_path: str) -> str:
        Path(dest_path).parent.mkdir(parents=True, exist_ok=True)
        resp = requests.get(url, timeout=120, stream=True)
        resp.raise_for_status()
        with open(dest_path, "wb") as f:
            for chunk in resp.iter_content(chunk_size=8192):
                f.write(chunk)
        return dest_path

    def get_balance(self) -> float:
        resp = self._request("GET", "balance")
        return float(resp.json().get("data", {}).get("balance", 0))

    def generate_one(
        self,
        prompt: str,
        avatar_url: str,
        output_path: str,
        size: Optional[Tuple[int, int]] = None,
    ) -> dict:
        t0 = time.time()
        try:
            body = {
                "images": [avatar_url],
                "prompt": prompt,
                "enable_sync_mode": False,
                "enable_base64_output": False,
            }
            if size:
                body["size"] = f"{size[0]}*{size[1]}"
            resp = self._request("POST", IMAGE_MODEL, json=body)
            task_id = resp.json()["data"]["id"]
            image_url = self._poll(task_id)
            self._download(image_url, output_path)
            return {"ok": True, "output_path": output_path, "duration_s": round(time.time() - t0, 1)}
        except WaveSpeedError as e:
            return {"ok": False, "error_code": e.code, "error_message": e.message, "duration_s": round(time.time() - t0, 1)}
        except Exception as e:
            return {"ok": False, "error_code": "unexpected", "error_message": str(e), "duration_s": round(time.time() - t0, 1)}

    def batch_generate(
        self,
        jobs: list,
        avatar_url: str,
        output_dir: str,
        size: Optional[Tuple[int, int]] = None,
        max_concurrent: int = 5,
        progress_callback: Optional[Callable[[int, int, str], None]] = None,
        checkpoint_path: Optional[str] = None,
    ) -> dict:
        Path(output_dir).mkdir(parents=True, exist_ok=True)
        lock_path = Path(output_dir) / ".batch.lock"
        lock_fd = open(lock_path, "w")
        try:
            _lock_file(lock_fd)
        except (BlockingIOError, OSError):
            lock_fd.close()
            raise WaveSpeedError(
                "batch_already_running",
                f"Another batch is running on '{output_dir}'. No requests sent.",
            )

        lock_fd.write(
            f"pid={os.getpid()}\n"
            f"started_at={datetime.now().isoformat()}\n"
            f"n_jobs={len(jobs)}\n"
        )
        lock_fd.flush()

        try:
            completed = {}
            if checkpoint_path and Path(checkpoint_path).exists():
                with open(checkpoint_path) as f:
                    completed = json.load(f)

            results = []
            done_count = [0]
            t0 = time.time()

            def _worker(job):
                filename = job["filename"]
                output_path = os.path.join(output_dir, filename)
                if filename in completed and Path(completed[filename].get("output_path", "")).exists():
                    return {"skipped": True, "filename": filename, **completed[filename]}
                r = self.generate_one(job["prompt"], avatar_url, output_path, size=size)
                r["filename"] = filename
                r["metadata"] = job.get("metadata", {})
                if checkpoint_path:
                    completed[filename] = r
                    with open(checkpoint_path, "w") as f:
                        json.dump(completed, f, indent=2)
                return r

            with ThreadPoolExecutor(max_workers=max_concurrent) as pool:
                futures = {pool.submit(_worker, j): j for j in jobs}
                for fut in as_completed(futures):
                    r = fut.result()
                    results.append(r)
                    done_count[0] += 1
                    if progress_callback:
                        label = r.get("filename", "?")
                        if r.get("ok"):
                            label = f"OK {label}"
                        elif r.get("skipped"):
                            label = f"SKIP {label} (already done)"
                        else:
                            label = f"FAIL {label}: {r.get('error_message', 'error')}"
                        try:
                            progress_callback(done_count[0], len(jobs), label)
                        except Exception:
                            pass

            success = [r for r in results if r.get("ok")]
            failed = [r for r in results if not r.get("ok") and not r.get("skipped")]
            return {
                "success": success,
                "failed": failed,
                "duration_s": round(time.time() - t0, 1),
                "n_total": len(jobs),
                "n_success": len(success),
                "n_failed": len(failed),
            }
        finally:
            _unlock_file(lock_fd)
            try:
                lock_fd.close()
            except Exception:
                pass
            try:
                lock_path.unlink()
            except Exception:
                pass


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: py wavespeed_client.py <api_key> [balance]")
        sys.exit(1)
    key = sys.argv[1]
    client = WaveSpeedClient(key)
    cmd = sys.argv[2] if len(sys.argv) > 2 else "balance"
    if cmd == "balance":
        print(f"Balance: ${client.get_balance():.4f}")
    else:
        print(f"Unknown command: {cmd}")

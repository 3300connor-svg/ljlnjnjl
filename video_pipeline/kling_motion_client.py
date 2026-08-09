"""
kling_motion_client.py — Kling 3.0 Std Motion Control client.

Model: kwaivgi/kling-v3.0-std/motion-control
Pricing: $0.378 (≤3s) / $0.63 (5s) / $1.26 (10s) / $3.78 (30s max)

Takes a character image + driving video, transfers the motion.
character_orientation="video" supports up to 30s.
"""

from pathlib import Path

from wavespeed_base import WaveSpeedJobClient

STD_MODEL     = "kwaivgi/kling-v3.0-std/motion-control"
PRO_MODEL     = "kwaivgi/kling-v3.0-pro/motion-control"
POLL_INTERVAL = 10
MAX_POLL_SECS = 600


class KlingMotionClient(WaveSpeedJobClient):
    def __init__(self, api_key: str, model: str = STD_MODEL):
        super().__init__(api_key, poll_interval=POLL_INTERVAL, max_poll_secs=MAX_POLL_SECS)
        self.model = model

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

        task_id = self.submit(self.model, body)
        if progress_cb:
            progress_cb(f"Processing (task {task_id[:8]}...)  polling every {POLL_INTERVAL}s")

        out_url = self.poll(task_id, model="Kling")

        if progress_cb:
            progress_cb("Downloading output video...")
        self.download(out_url, output_path, timeout=300)

        size_kb = Path(output_path).stat().st_size // 1024
        if progress_cb:
            progress_cb(f"Done ({size_kb} KB)")
        return output_path

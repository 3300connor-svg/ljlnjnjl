"""
wavespeed_upscaler.py — Image upscaling via wavespeed-ai/real-esrgan.

Upscales the swap image before it's passed to Kling, giving Kling a higher
quality input and producing sharper, more detailed final video.
"""

from config import WAVESPEED_API_KEY
from wavespeed_base import WaveSpeedJobClient

MODEL         = "wavespeed-ai/real-esrgan"
POLL_INTERVAL = 3
MAX_POLL_SECS = 120


class WaveSpeedUpscaler(WaveSpeedJobClient):
    def __init__(self, api_key: str = WAVESPEED_API_KEY):
        super().__init__(api_key, poll_interval=POLL_INTERVAL, max_poll_secs=MAX_POLL_SECS)

    def upscale(self, image_url: str, output_path: str, progress_cb=None) -> str:
        """
        Upscale image_url with Real-ESRGAN, download result to output_path.
        Returns output_path on success.
        """
        if progress_cb:
            progress_cb("Submitting to WaveSpeed upscaler...")

        task_id = self.submit(MODEL, {"image": image_url})

        if progress_cb:
            progress_cb(f"Upscaling (task {task_id[:8]}...)...")

        image_url_out = self.poll(task_id, model="Upscaler")

        if progress_cb:
            progress_cb("Downloading upscaled image...")
        return self.download(image_url_out, output_path, timeout=60)

"""
catbox_uploader.py — IPC bridge for Chrome-based Catbox uploads.

bot.py writes temp/catbox_request.json with the local file path.
Claude Code handles it via claude-in-chrome on catbox.moe.
Result URL is written to temp/catbox_result.json.
"""

import json
import time
from pathlib import Path

_BASE           = Path(__file__).parent
REQUEST_FILE    = _BASE / "temp" / "catbox_request.json"
RESULT_FILE     = _BASE / "temp" / "catbox_result.json"
TIMEOUT         = 300   # 5 minutes


def upload_via_chrome(local_path: str, progress_cb=None) -> str:
    tmp = _BASE / "temp"
    tmp.mkdir(exist_ok=True)

    REQUEST_FILE.unlink(missing_ok=True)
    RESULT_FILE.unlink(missing_ok=True)

    REQUEST_FILE.write_text(
        json.dumps({"file": str(Path(local_path).resolve())}),
        encoding="utf-8",
    )

    if progress_cb:
        progress_cb("Chrome agent uploading to Catbox...")

    deadline = time.time() + TIMEOUT
    while time.time() < deadline:
        if RESULT_FILE.exists():
            try:
                result = json.loads(RESULT_FILE.read_text(encoding="utf-8-sig"))
            except json.JSONDecodeError:
                time.sleep(0.5)
                continue
            RESULT_FILE.unlink(missing_ok=True)
            REQUEST_FILE.unlink(missing_ok=True)
            if result.get("error"):
                raise RuntimeError(result["error"])
            return result["url"]
        time.sleep(2)

    REQUEST_FILE.unlink(missing_ok=True)
    raise RuntimeError(f"Catbox Chrome upload timed out after {TIMEOUT}s")

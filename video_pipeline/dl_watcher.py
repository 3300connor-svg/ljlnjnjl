"""
dl_watcher.py — Watches for download + catbox upload requests.
Claude Code monitors this script's output via the Monitor tool.
"""

import json
import time
from pathlib import Path

BASE = Path(__file__).parent / "temp"
BASE.mkdir(exist_ok=True)

DL_REQUEST     = BASE / "dl_request.json"
CATBOX_REQUEST = BASE / "catbox_request.json"

print("[watcher] Ready — watching for requests...", flush=True)

seen_dl     = None
seen_catbox = None

while True:
    try:
        # Download requests
        if DL_REQUEST.exists():
            content = DL_REQUEST.read_text(encoding="utf-8-sig").strip()
            if content and content != seen_dl:
                seen_dl = content
                print(f"DOWNLOAD_NEEDED:{content}", flush=True)
        else:
            seen_dl = None

        # Catbox upload requests
        if CATBOX_REQUEST.exists():
            content = CATBOX_REQUEST.read_text(encoding="utf-8-sig").strip()
            if content and content != seen_catbox:
                seen_catbox = content
                print(f"CATBOX_NEEDED:{content}", flush=True)
        else:
            seen_catbox = None

    except Exception as e:
        print(f"[watcher] error: {e}", flush=True)

    time.sleep(1)

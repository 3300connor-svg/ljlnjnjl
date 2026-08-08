"""
bot.py — Telegram bot for the Instagram → Kling 3.0 pipeline.

Send an Instagram URL → fully automatic pipeline:
  1. Download via fastdl.app
  2. Confirmation message (refs, models, cost, settings)
  3. Upload raw video to Catbox
  4. Extract best frame
  5. Seedream 4.5 face/body swap (frame + face ref + body ref)
  6. Upload swapped image to Catbox
  7. Trim video to 30s if needed, re-upload if trimmed
  8. Kling 3.0 Motion Control
  9. Pick trending song
  10. Virality score (if ANTHROPIC_API_KEY set)
  11. Send result video to Telegram

Commands:
  !help     → list commands
  !status   → what's running
  !cancel   → stop all active pipelines
  !balance  → WaveSpeed balance
"""

import contextlib
import json
import queue
import re
import sys
import time
import threading
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import requests

sys.path.insert(0, str(Path(__file__).parent))

from config import (
    TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID,
    WAVESPEED_API_KEY, WAVESPEED_BASE,
    FACE_REFERENCE_URL, BODY_REFERENCE_URL,
    DEFAULT_IMAGE_PROMPT, DEFAULT_KLING_PROMPT,
    OUTPUT_DIR, TEMP_DIR, MAX_VIDEO_SECONDS,
    FALLBACK_URLS,
)

URL_RE             = re.compile(r"https?://\S+")
INSTAGRAM_DOMAINS  = ("instagram.com", "instagr.am")
TG_BASE            = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}"
MAX_TG_VIDEO_BYTES = 50 * 1024 * 1024   # Telegram bot sendVideo limit

_executor      = ThreadPoolExecutor(max_workers=3)
_active_jobs   : dict[str, threading.Event] = {}   # url → cancel_event
_submitted_urls: set[str] = set()                   # dedup guard
_lock       = threading.Lock()
_reply_lock = threading.Lock()
_reply_queue: "queue.Queue | None" = None           # set when pipeline awaits user input

_MSG_LOG_FILE = Path(TEMP_DIR) / "sent_message_ids.json"
_CLEAR_FLAG   = Path(TEMP_DIR) / "clear_on_reboot.flag"


def _log_msg_id(msg_id: int):
    """Append a sent message ID to the persistent log."""
    if not msg_id:
        return
    try:
        Path(TEMP_DIR).mkdir(exist_ok=True)
        ids = []
        if _MSG_LOG_FILE.exists():
            try:
                ids = json.loads(_MSG_LOG_FILE.read_text())
            except Exception:
                ids = []
        ids.append(msg_id)
        _MSG_LOG_FILE.write_text(json.dumps(ids))
    except Exception:
        pass


def _clear_chat_history():
    """Delete all bot-sent messages logged in _MSG_LOG_FILE."""
    if not _MSG_LOG_FILE.exists():
        return
    try:
        ids = json.loads(_MSG_LOG_FILE.read_text())
    except Exception:
        ids = []
    deleted = 0
    for mid in ids:
        try:
            r = requests.post(
                f"{TG_BASE}/deleteMessage",
                json={"chat_id": TELEGRAM_CHAT_ID, "message_id": mid},
                timeout=10,
            )
            if r.json().get("result"):
                deleted += 1
        except Exception:
            pass
    try:
        _MSG_LOG_FILE.unlink(missing_ok=True)
        _CLEAR_FLAG.unlink(missing_ok=True)
    except Exception:
        pass
    print(f"[bot] Cleared {deleted}/{len(ids)} messages")


class _PipelineCancelled(Exception):
    pass


# ── Telegram helpers ──────────────────────────────────────────────────────────

def _tg(method: str, **kwargs) -> dict:
    for attempt in range(4):
        try:
            r = requests.post(f"{TG_BASE}/{method}", json={**kwargs}, timeout=30)
            return r.json()
        except (requests.exceptions.ConnectionError,
                requests.exceptions.Timeout) as e:
            if attempt < 3:
                wait = 2 ** attempt   # 1s, 2s, 4s
                print(f"[tg] {method} connection error (attempt {attempt+1}/4), retrying in {wait}s: {e}")
                time.sleep(wait)
            else:
                print(f"[tg] {method} failed after 4 attempts: {e}")
                return {}
        except Exception as e:
            print(f"[tg] {method} failed: {e}")
            return {}
    return {}


def send(text: str):
    r = _tg("sendMessage", chat_id=TELEGRAM_CHAT_ID, text=text)
    _log_msg_id(r.get("result", {}).get("message_id", 0))


def send_with_id(text: str) -> int:
    r = _tg("sendMessage", chat_id=TELEGRAM_CHAT_ID, text=text)
    mid = r.get("result", {}).get("message_id", 0)
    _log_msg_id(mid)
    return mid


def edit_message(msg_id: int, text: str):
    if not msg_id:
        return
    _tg("editMessageText", chat_id=TELEGRAM_CHAT_ID, message_id=msg_id, text=text)


def send_video(path: str, caption: str = ""):
    """Send video. Falls back to a Catbox link if the file exceeds 50MB."""
    from downloader import upload_catbox
    size = Path(path).stat().st_size if Path(path).exists() else 0
    if size > MAX_TG_VIDEO_BYTES:
        send(
            f"⚠️ Output is {size // 1024 // 1024}MB — over Telegram's 50MB limit.\n"
            f"Uploading to Catbox instead..."
        )
        try:
            url = upload_catbox(path, on_fallback=lambda m: send(m))
            send(f"✅ Download link:\n{url}\n\n{caption}")
        except Exception as e:
            send(f"❌ Catbox also failed: {e}")
        return
    with open(path, "rb") as f:
        try:
            requests.post(
                f"{TG_BASE}/sendVideo",
                data={"chat_id": TELEGRAM_CHAT_ID, "caption": caption},
                files={"video": f},
                timeout=300,
            )
        except Exception as e:
            send(f"❌ sendVideo failed: {e}")


def send_photo_file(path: str, caption: str = "", reply_markup: dict | None = None) -> dict:
    data: dict = {"chat_id": TELEGRAM_CHAT_ID, "caption": caption}
    if reply_markup:
        data["reply_markup"] = json.dumps(reply_markup)
    with open(path, "rb") as f:
        try:
            r = requests.post(
                f"{TG_BASE}/sendPhoto",
                data=data,
                files={"photo": f},
                timeout=60,
            )
            resp = r.json()
            _log_msg_id(resp.get("result", {}).get("message_id", 0))
            return resp
        except Exception as e:
            print(f"[tg] sendPhoto failed: {e}")
            return {}


def send_with_kb(text: str, kb: dict, parse_mode: str = "HTML") -> int:
    r = _tg("sendMessage", chat_id=TELEGRAM_CHAT_ID, text=text,
            parse_mode=parse_mode, reply_markup=kb)
    mid = r.get("result", {}).get("message_id", 0)
    _log_msg_id(mid)
    return mid


# ── Inline keyboards ──────────────────────────────────────────────────────────

_KB_CONFIRM = {"inline_keyboard": [[
    {"text": "✅  GO",            "callback_data": "go"},
    {"text": "❌  CANCEL",        "callback_data": "cancel"},
    {"text": "✏️  CUSTOM PROMPT", "callback_data": "custom_prompt"},
]]}

_KB_SWAP = {"inline_keyboard": [
    [
        {"text": "✅  GO",     "callback_data": "go"},
        {"text": "🔄  RETRY",  "callback_data": "retry"},
        {"text": "❌  CANCEL", "callback_data": "cancel"},
    ],
    [
        {"text": "✏️  EDIT PROMPT",       "callback_data": "edit_prompt"},
        {"text": "➕  ADDITIONAL PROMPT", "callback_data": "custom_prompt"},
    ],
]}

_KB_KLING = {"inline_keyboard": [
    [
        {"text": "✅  GO",     "callback_data": "go"},
        {"text": "❌  CANCEL", "callback_data": "cancel"},
    ],
    [{"text": "✏️  ADDITIONAL PROMPT", "callback_data": "custom_prompt"}],
]}

_KB_RETRY_CANCEL = {"inline_keyboard": [[
    {"text": "🔄  RETRY",  "callback_data": "retry"},
    {"text": "❌  CANCEL", "callback_data": "cancel"},
]]}

_KB_UPSCALE = {"inline_keyboard": [[
    {"text": "📐  2x UPSCALE", "callback_data": "upscale_2x"},
    {"text": "⏭️  SKIP",       "callback_data": "upscale_skip"},
]]}

_KB_META = {"inline_keyboard": [[
    {"text": "📱  APPLY iPHONE METADATA", "callback_data": "meta_yes"},
    {"text": "⏭️  SKIP",                  "callback_data": "meta_no"},
]]}


# ── Typing indicator ──────────────────────────────────────────────────────────

@contextlib.contextmanager
def _typing():
    """Show Telegram 'typing…' animation until the with-block exits."""
    stop = threading.Event()
    def _loop():
        while not stop.wait(4):
            try:
                requests.post(f"{TG_BASE}/sendChatAction",
                              json={"chat_id": TELEGRAM_CHAT_ID, "action": "typing"},
                              timeout=5)
            except Exception:
                pass
    requests.post(f"{TG_BASE}/sendChatAction",
                  json={"chat_id": TELEGRAM_CHAT_ID, "action": "typing"}, timeout=5)
    t = threading.Thread(target=_loop, daemon=True)
    t.start()
    try:
        yield
    finally:
        stop.set()


# ── WaveSpeed balance helper ──────────────────────────────────────────────────

def _get_balance() -> float:
    try:
        r = requests.get(
            f"{WAVESPEED_BASE}/api/v3/user/balance",
            headers={"Authorization": f"Bearer {WAVESPEED_API_KEY}"},
            timeout=10,
        )
        return float(r.json().get("data", {}).get("balance", -1))
    except Exception:
        return -1.0


def get_updates(offset: int) -> list[dict]:
    r = requests.get(
        f"{TG_BASE}/getUpdates",
        params={"offset": offset, "timeout": 25,
                "allowed_updates": ["message", "callback_query"]},
        timeout=40,
    )
    if not r.ok:
        raise RuntimeError(f"getUpdates HTTP {r.status_code}")
    return r.json().get("result", [])


def download_tg_file(file_id: str, dest_path: str) -> str:
    info      = _tg("getFile", file_id=file_id)
    file_path = info.get("result", {}).get("file_path", "")
    url       = f"https://api.telegram.org/file/bot{TELEGRAM_BOT_TOKEN}/{file_path}"
    Path(dest_path).parent.mkdir(parents=True, exist_ok=True)
    with requests.get(url, stream=True, timeout=180) as r:
        r.raise_for_status()
        with open(dest_path, "wb") as f:
            for chunk in r.iter_content(65536):
                f.write(chunk)
    return dest_path


# ── Error fallback: open service in browser ───────────────────────────────────

def _wait_reply(timeout: int = 120) -> str:
    """Block the calling (pipeline) thread until the user sends a message or timeout."""
    global _reply_queue
    rq = queue.Queue()
    with _reply_lock:
        _reply_queue = rq
    try:
        return rq.get(timeout=timeout)
    except queue.Empty:
        return ""
    finally:
        with _reply_lock:
            _reply_queue = None


_CHROME_PATHS = [
    r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
    r"C:\Users\Connor\AppData\Local\Google\Chrome\Application\chrome.exe",
]


_CHROME_PROFILE = "Profile 24"   # Connor (CLAUDE)


def _open_in_browser(url: str) -> str:
    """
    Open url in Chrome with the Connor (CLAUDE) profile.
    Falls back to system default browser if Chrome isn't found.
    Returns a string describing which browser was used.
    """
    for path in _CHROME_PATHS:
        if Path(path).exists():
            subprocess.Popen([path, f"--profile-directory={_CHROME_PROFILE}", url])
            return "Chrome — Connor (CLAUDE) profile"
    webbrowser.open(url)
    return "system default browser"


def _open_fallback(service: str, extra_msg: str = ""):
    url = FALLBACK_URLS.get(service, "")
    msg = f"❌ {service} failed"
    if extra_msg:
        msg += f": {extra_msg[:200]}"
    if url:
        browser = _open_in_browser(url)
        msg += f"\nOpened {url}\nin: {browser}"
        send(msg)
    else:
        send(msg)


# ── Helpers ───────────────────────────────────────────────────────────────────

def _is_instagram_url(url: str) -> bool:
    return any(d in url for d in INSTAGRAM_DOMAINS)


def _kling_cost(duration_s: float) -> str:
    capped = min(duration_s, 30)
    cost   = round(capped * 0.063, 3)
    return f"~${cost:.3f}"


# ── Progress tracker ──────────────────────────────────────────────────────────

_STEPS = [
    "Download",
    "Upload to Catbox",
    "Extract best frame",
    "Seedream 4.5 swap",
    "Upload image to Catbox",
    "Trim & upload video",
    "Kling 3.0 Motion Control",
    "Trending audio",
    "Virality score",
]


def _step_text(step_idx: int, detail: str = "", done: bool = False) -> str:
    title = "✅ Pipeline done!\n" if done else "🎬 Pipeline running\n"
    lines = [title]
    for i, label in enumerate(_STEPS):
        if done or i < step_idx:
            lines.append(f"✅ {label}")
        elif i == step_idx:
            d = f"  — {detail[:60]}" if detail else ""
            lines.append(f"⏳ {label}{d}")
        else:
            lines.append(f"⬜ {label}")
    pct    = 100 if done else round((step_idx + 1) / len(_STEPS) * 100)
    filled = round(pct / 100 * 12)
    bar    = f"{'█' * filled}{'░' * (12 - filled)}  {pct}%"
    lines.append(f"\n{bar}")
    return "\n".join(lines)


# ── Main pipeline ─────────────────────────────────────────────────────────────

def _run_pipeline(local_path: str, label: str, cancel_event: threading.Event, source_url: str = ""):
    from downloader import upload_catbox, upload_for_wavespeed, get_video_duration, trim_video
    from frame_extractor import extract_best_frame
    from seedream_client import SeedreamClient
    from kling_motion_client import KlingMotionClient
    from trending_fetcher import fetch_trending_list
    import uuid
    import random

    def _check():
        if cancel_event.is_set():
            raise _PipelineCancelled()

    uid          = uuid.uuid4().hex[:8]
    tmp          = Path(TEMP_DIR)
    frame_path   = str(tmp / f"{uid}_frame.jpg")
    swap_path    = str(tmp / f"{uid}_swap.jpg")
    trimmed_path = str(tmp / f"{uid}_trimmed.mp4")
    out_path     = str(Path(OUTPUT_DIR) / f"{uid}_{int(time.time())}.mp4")
    tmp.mkdir(exist_ok=True)
    Path(OUTPUT_DIR).mkdir(exist_ok=True)

    msg_id = send_with_id("⬇️ Download complete. Extracting best frame...")

    try:
        duration = get_video_duration(local_path)
    except Exception:
        duration = 0.0

    try:
        # ── Step 1: Extract best frame (face priority) ────────────────────────
        _check()
        try:
            extract_best_frame(local_path, frame_path)
        except Exception as e:
            send(f"❌ Frame extraction failed: {e}")
            return

        _dur_str = f"{int(duration // 60)}:{int(duration % 60):02d}" if duration >= 60 else f"{duration:.1f}s"
        _link    = f'<a href="{source_url}">{source_url[:60]}</a>' if source_url else label[:60]

        _caption = (
            f"Image 1: Best frame extraction\n"
            f"Image 2: Model reference image\n\n"
            f"{_link}  ·  {_dur_str}\n\n"
            f"Prompt:\n{DEFAULT_IMAGE_PROMPT}"
        )
        _media = json.dumps([
            {"type": "photo", "media": "attach://frame",
             "caption": _caption, "parse_mode": "HTML"},
            {"type": "photo", "media": FACE_REFERENCE_URL},
        ])
        _album_sent = False
        try:
            with open(frame_path, "rb") as _f:
                _r = requests.post(
                    f"{TG_BASE}/sendMediaGroup",
                    data={"chat_id": TELEGRAM_CHAT_ID, "media": _media},
                    files={"frame": ("frame.jpg", _f, "image/jpeg")},
                    timeout=60,
                )
            _album_sent = bool(_r.json().get("result"))
        except Exception:
            pass

        if not _album_sent:
            send_photo_file(frame_path, caption=f"Image 1: Best frame extraction  ·  {_dur_str}")
            _tg("sendPhoto", chat_id=TELEGRAM_CHAT_ID, photo=FACE_REFERENCE_URL,
                caption="Image 2: Model reference image")

        _bal_swap = _get_balance()
        _bal_swap_str = f"${_bal_swap:.3f}" if _bal_swap >= 0 else "?"
        send_with_kb(
            f"Confirm to proceed:\n💰 Seedream 4.5: <b>$0.04</b>   Balance: {_bal_swap_str}",
            _KB_CONFIRM,
        )
        action = _wait_reply(timeout=180)
        action_lower = action.strip().lower()
        if not action or action_lower == "cancel":
            send("❌ Cancelled.")
            raise _PipelineCancelled()
        # additional text layers on top of default prompt
        seedream_prompt = (DEFAULT_IMAGE_PROMPT if action_lower == "go"
                           else DEFAULT_IMAGE_PROMPT + " " + action.strip())

        # ── Step 2: Upload video + frame for WaveSpeed ────────────────────────
        _check()
        edit_message(msg_id, _step_text(1, "uploading video..."))
        try:
            video_ws_url = upload_for_wavespeed(local_path, progress_cb=lambda m: edit_message(msg_id, _step_text(1, m)))
            print(f"[pipeline] video ws url: {video_ws_url}")
        except Exception as e:
            send(f"❌ Video upload failed: {str(e)[:300]}")
            return

        _check()
        edit_message(msg_id, _step_text(2, "uploading frame..."))
        try:
            frame_ws_url = upload_for_wavespeed(frame_path, progress_cb=lambda m: edit_message(msg_id, _step_text(2, m)))
            print(f"[pipeline] frame ws url: {frame_ws_url}")
        except Exception as e:
            send(f"❌ Frame upload failed: {str(e)[:300]}")
            return

        # ── Step 3: Seedream 4.5 face + hair swap ────────────────────────────────
        _check()
        seedream       = SeedreamClient(WAVESPEED_API_KEY)
        current_prompt = seedream_prompt

        while True:
            _check()
            edit_message(msg_id, _step_text(3, "generating face + hair swap..."))
            _swap_bal_before = _get_balance()
            try:
                with _typing():
                    seedream.generate(
                        current_prompt,
                        FACE_REFERENCE_URL,
                        swap_path,
                        scene_url=frame_ws_url,
                        progress_cb=lambda m: edit_message(msg_id, _step_text(3, m)),
                    )
            except Exception as e:
                _err_bal_str = f"   Balance: ${_swap_bal_before:.3f}" if _swap_bal_before >= 0 else ""
                send_with_kb(
                    f"❌ WaveSpeed error: {str(e)[:200]}\n\n💰 Retry costs ~$0.04{_err_bal_str}",
                    _KB_RETRY_CANCEL,
                )
                action = _wait_reply(timeout=120)
                if action.strip().lower() != "retry":
                    raise _PipelineCancelled()
                Path(swap_path).unlink(missing_ok=True)
                continue

            _swap_bal_after = _get_balance()
            _swap_cost_str = (
                f"${_swap_bal_before - _swap_bal_after:.4f}"
                if _swap_bal_before >= 0 and _swap_bal_after >= 0
                else "~$0.04"
            )
            _swap_remain_str = f"   Balance: ${_swap_bal_after:.3f}" if _swap_bal_after >= 0 else ""
            send_photo_file(
                swap_path,
                caption=(
                    f"🎭 Face + hair swap  ·  {_swap_cost_str}{_swap_remain_str}\n"
                    f"⚠️ Retry or additional prompt generates a new image (~$0.04 each)\n\n"
                    f"Prompt:\n{current_prompt}"
                ),
                reply_markup=_KB_SWAP,
            )
            action = _wait_reply(timeout=180)
            action_lower = action.strip().lower()

            if not action or action_lower == "cancel":
                send("❌ Cancelled.")
                raise _PipelineCancelled()
            elif action_lower == "go":
                break
            elif action_lower == "retry":
                Path(swap_path).unlink(missing_ok=True)
                continue
            elif action_lower == "edit_prompt":
                _tg("sendMessage",
                    chat_id=TELEGRAM_CHAT_ID,
                    text=(
                        f"✏️ <b>Current prompt</b> — copy, paste and edit:\n\n"
                        f"<code>{current_prompt}</code>"
                    ),
                    parse_mode="HTML",
                    reply_markup={
                        "force_reply": True,
                        "input_field_placeholder": "Paste and edit the prompt above...",
                    })
                edited = _wait_reply(timeout=300)
                if edited and edited.strip().lower() not in ("", "cancel"):
                    current_prompt = edited.strip()
                Path(swap_path).unlink(missing_ok=True)
                continue
            else:
                # Additional prompt — stacks on top of current accumulated prompt
                current_prompt = current_prompt + " " + action.strip()
                Path(swap_path).unlink(missing_ok=True)
                continue

        # ── Step 4: Optional upscale swap image, then upload ─────────────────
        _check()
        _upscale_bal_str = f"   Balance: ${_swap_bal_after:.3f}" if _swap_bal_after >= 0 else ""
        send_with_kb(f"📐 Upscale swap image with Real-ESRGAN before Kling?\n(improves skin texture + detail){_upscale_bal_str}", _KB_UPSCALE)
        up_choice = _wait_reply(timeout=120)
        if up_choice.strip().lower() == "upscale_2x":
            try:
                from wavespeed_upscaler import WaveSpeedUpscaler
                upscaled_path = swap_path.replace(".jpg", "_upscaled.jpg")
                edit_message(msg_id, _step_text(4, "upscaling with Real-ESRGAN..."))
                # Upload swap first to get a URL for the upscaler
                _tmp_url = upload_for_wavespeed(swap_path, progress_cb=lambda m: edit_message(msg_id, _step_text(4, m)))
                with _typing():
                    WaveSpeedUpscaler().upscale(
                        _tmp_url, upscaled_path,
                        progress_cb=lambda m: edit_message(msg_id, _step_text(4, m)),
                    )
                # Show the upscaled result
                send_photo_file(upscaled_path, caption="📐 Upscaled swap image (Real-ESRGAN)")
                swap_path = upscaled_path
            except Exception as e:
                send(f"⚠️ Upscale failed ({e}) — continuing with original")

        edit_message(msg_id, _step_text(4, "uploading swap image..."))
        try:
            swap_ws_url = upload_for_wavespeed(swap_path, progress_cb=lambda m: edit_message(msg_id, _step_text(4, m)))
            print(f"[pipeline] swap ws url: {swap_ws_url}")
        except Exception as e:
            send(f"❌ Swap image upload failed: {str(e)[:300]}")
            return

        _check()
        edit_message(msg_id, _step_text(5, "trimming video..."))
        try:
            trimmed     = trim_video(local_path, trimmed_path, max_seconds=MAX_VIDEO_SECONDS)
            was_trimmed = (trimmed == trimmed_path)
        except Exception as e:
            send(f"❌ Trim failed: {e}")
            return

        if was_trimmed:
            _check()
            edit_message(msg_id, _step_text(5, "re-uploading trimmed video..."))
            try:
                video_ws_url = upload_for_wavespeed(trimmed_path, progress_cb=lambda m: edit_message(msg_id, _step_text(5, m)))
            except Exception as e:
                send(f"❌ Trimmed video upload failed: {str(e)[:300]}")
                return

        # ── Step 6: Kling confirmation then generate ──────────────────────────
        _check()
        try:
            actual_dur = get_video_duration(trimmed if was_trimmed else local_path)
        except Exception:
            actual_dur = duration
        actual_cost = _kling_cost(actual_dur)

        # Balance before Kling (for exact cost delta)
        bal_before = _get_balance()

        # Pre-Kling virality estimate from swap image
        virality_preview = ""
        try:
            from virality_ranker import rank_videos
            ranked = rank_videos([swap_path])
            if ranked and not ranked[0].get("error"):
                sc = ranked[0]
                virality_preview = (
                    f"\n📊 Virality estimate: {sc.get('total', '?')}/10"
                    f"  ({sc.get('reasoning', '')[:80]})"
                )
        except Exception:
            pass

        kling        = KlingMotionClient(WAVESPEED_API_KEY)
        kling_prompt = DEFAULT_KLING_PROMPT

        bal_str = f"${bal_before:.3f}" if bal_before >= 0 else "?"

        while True:
            _check()
            send_with_kb(
                f"🎬 <b>Kling 3.0 Motion Control</b>\n\n"
                f"🖼  Image: face + hair swap\n"
                f"🎥  Video: {label[:40]}{' ✂️' if was_trimmed else ''}  ·  {actual_dur:.1f}s\n"
                f"💰  Est. cost: {actual_cost}   Balance: {bal_str}\n"
                f"🔊  Sound: preserved  ·  Mode: motion control\n"
                f"{virality_preview}\n\n"
                f"Prompt:\n{kling_prompt}",
                _KB_KLING,
            )
            reply       = _wait_reply(timeout=120)
            reply_lower = reply.strip().lower()

            if not reply or reply_lower == "cancel":
                send("❌ Kling cancelled.")
                raise _PipelineCancelled()

            if reply_lower != "go":
                kling_prompt = DEFAULT_KLING_PROMPT + " " + reply.strip()

            _check()
            edit_message(msg_id, _step_text(6, "submitting to Kling 3.0..."))
            try:
                with _typing():
                    kling.motion_control(
                        swap_ws_url,
                        video_ws_url,
                        out_path,
                        orientation="video",
                        keep_sound=True,
                        prompt=kling_prompt,
                        progress_cb=lambda m: edit_message(msg_id, _step_text(6, m)),
                    )
                break
            except Exception as e:
                send_with_kb(f"❌ Kling error: {str(e)[:200]}", _KB_RETRY_CANCEL)
                action = _wait_reply(timeout=60)
                if action.strip().lower() != "retry":
                    raise _PipelineCancelled()

        # Actual cost from balance delta
        bal_after   = _get_balance()
        actual_spend = (
            f"${bal_before - bal_after:.4f}"
            if bal_before >= 0 and bal_after >= 0
            else actual_cost
        )

        # ── Step 7: Trending audio pick ───────────────────────────────────────
        _check()
        edit_message(msg_id, _step_text(7, "fetching trending songs..."))
        audio_name = None
        try:
            tracks = fetch_trending_list()
            if tracks:
                t          = random.choice(tracks[:20])
                audio_name = f"{t['title']} — {t['artist']}" if t.get("artist") else t["title"]
        except Exception as e:
            print(f"[pipeline] trending fetch failed: {e}")

        # ── Step 8: Virality score ─────────────────────────────────────────────
        _check()
        edit_message(msg_id, _step_text(8, "scoring virality..."))
        score_text = ""
        try:
            from virality_ranker import rank_videos
            ranked = rank_videos([out_path])
            if ranked and not ranked[0].get("error"):
                sc = ranked[0]
                score_text = (
                    f"\n\n📊 Virality: {sc.get('total', '?')}/10\n"
                    f"  Emotional: {sc.get('emotional_intensity', '?')}/10\n"
                    f"  Hook: {sc.get('viral_hook', '?')}/10\n"
                    f"  Quality: {sc.get('visual_quality', '?')}/10\n"
                    f"  Controversy: {sc.get('controversy', '?')}/10\n"
                    f"  {sc.get('reasoning', '')}"
                )
        except Exception as e:
            print(f"[pipeline] virality score failed: {e}")

        # ── Done ──────────────────────────────────────────────────────────────
        edit_message(msg_id, _step_text(0, done=True))

        current_out = out_path

        # ── Deliver video ─────────────────────────────────────────────────────
        caption = f"✅ Pipeline complete!  Cost: {actual_spend}"
        if audio_name:
            caption += f"\n\n🎵 Suggested audio: {audio_name}"
        caption += score_text
        send_video(current_out, caption=caption)

        # ── Optional: iPhone metadata treatment ───────────────────────────────
        send_with_kb(
            "📱 Apply iPhone metadata + watermark disruption?",
            _KB_META,
        )
        meta_reply = _wait_reply(timeout=180)
        if not meta_reply or meta_reply.strip().lower() in ("meta_no", "skip"):
            send("⏭️ Metadata skipped.")
        elif meta_reply.strip().lower() in ("meta_yes", "yes"):
            try:
                from metadata_spoofer import spoof
                meta_path = current_out.replace(".mp4", "_meta.mp4")
                edit_message(msg_id, "📱 Applying iPhone metadata...")
                with _typing():
                    spoof(current_out, meta_path)
                send_video(meta_path, caption="📱 iPhone metadata applied + watermark disrupted")
                try:
                    Path(meta_path).unlink(missing_ok=True)
                except Exception:
                    pass
            except Exception as e:
                send(f"❌ Metadata error: {e}")
        else:
            send("⏭️ Metadata skipped.")

    except _PipelineCancelled:
        edit_message(msg_id, "🛑 Cancelled.")
        send("🛑 Pipeline cancelled.")

    finally:
        for p in [local_path, frame_path, swap_path, trimmed_path]:
            try:
                Path(p).unlink(missing_ok=True)
            except Exception:
                pass


# ── Process a single URL ──────────────────────────────────────────────────────

def _process_single(url: str):
    from downloader import download_video
    import uuid

    cancel_event = threading.Event()

    with _lock:
        if url in _submitted_urls:
            send("⚠️ Already processing that URL.")
            return
        _submitted_urls.add(url)
        _active_jobs[url] = cancel_event

    try:
        label    = url.rstrip("/").split("?")[0][-40:]
        raw_path = str(Path(TEMP_DIR) / f"{uuid.uuid4().hex[:8]}_raw.mp4")
        Path(TEMP_DIR).mkdir(exist_ok=True)

        msg_id = send_with_id("⬇️ Downloading reel...")
        try:
            raw_path = download_video(url, raw_path, progress_cb=lambda m: edit_message(msg_id, f"⬇️ {m}")) or raw_path
        except Exception as e:
            send(f"❌ Download failed: {str(e)[:300]}")
            return

        send("✅ Video downloaded! Starting pipeline...")

        if cancel_event.is_set():
            send("🛑 Cancelled before pipeline started.")
            return

        _run_pipeline(raw_path, label, cancel_event, source_url=url)

    finally:
        with _lock:
            _active_jobs.pop(url, None)
            _submitted_urls.discard(url)


def _process_local_file(local_path: str, label: str = "video"):
    _run_pipeline(local_path, label, threading.Event())


def _process_batch(urls: list[str]):
    send(f"📋 Processing {len(urls)} URL(s) sequentially...")
    for i, url in enumerate(urls, 1):
        send(f"Starting #{i}/{len(urls)}")
        _process_single(url)


# ── Commands ──────────────────────────────────────────────────────────────────

_HELP_TEXT = (
    "🤖 Commands\n\n"
    "  !help    — this message\n"
    "  !status  — show active jobs\n"
    "  !cancel  — stop all running pipelines\n"
    "  !balance — WaveSpeed API balance\n"
    "  !clear   — delete all bot messages on next reboot\n\n"
    "Send an Instagram URL — or send a video file directly — to start the pipeline."
)


def _handle_command(text: str):
    t = text.strip()

    if t == "!help":
        send(_HELP_TEXT)
        return

    if t == "!status":
        with _lock:
            active = list(_active_jobs.keys())
        if active:
            lines = [f"⚙️ Processing {len(active)} job(s):"]
            for url in active:
                lines.append(f"  • {url[:60]}")
            send("\n".join(lines))
        else:
            send("Idle.")
        return

    if t == "!cancel":
        with _lock:
            jobs = dict(_active_jobs)
        if not jobs:
            send("Nothing running.")
            return
        for event in jobs.values():
            event.set()
        # Unblock any pipeline currently waiting for a user reply
        with _reply_lock:
            rq = _reply_queue
        if rq is not None:
            rq.put("cancel")
        send(f"🛑 Cancelling {len(jobs)} job(s)...")
        return

    if t == "!balance":
        try:
            r = requests.get(
                f"{WAVESPEED_BASE}/api/v3/user/balance",
                headers={"Authorization": f"Bearer {WAVESPEED_API_KEY}"},
                timeout=10,
            )
            bal = r.json().get("data", {}).get("balance", "?")
            send(f"💰 WaveSpeed balance: ${bal}")
        except Exception as e:
            send(f"Balance check failed: {e}")
        return

    if t == "!clear":
        Path(TEMP_DIR).mkdir(exist_ok=True)
        _CLEAR_FLAG.write_text("1")
        count = 0
        if _MSG_LOG_FILE.exists():
            try:
                count = len(json.loads(_MSG_LOG_FILE.read_text()))
            except Exception:
                pass
        send(f"🗑️ Clear scheduled — {count} message(s) will be deleted on next reboot.")
        return


# ── Message routing ───────────────────────────────────────────────────────────

def _handle_message(text: str):
    text = text.strip()

    # If a pipeline is waiting for a reply, route this message to it first
    with _reply_lock:
        rq = _reply_queue
    if rq is not None:
        rq.put(text)
        return

    # Telegram slash commands
    if text.lower().startswith("/start"):
        send("🤖 Pipeline online.\n\n" + _HELP_TEXT)
        return

    if text.startswith("!"):
        _handle_command(text)
        return

    urls    = URL_RE.findall(text)
    ig_urls = [u for u in urls if _is_instagram_url(u)]

    if ig_urls:
        if len(ig_urls) == 1:
            _executor.submit(_process_single, ig_urls[0])
        else:
            _executor.submit(_process_batch, ig_urls)
    elif urls:
        send("⚠️ No Instagram URLs detected. Send an instagram.com link to start the pipeline.")
    else:
        send("Send an Instagram URL to start the pipeline, or type !help for commands.")


# ── Main loop ─────────────────────────────────────────────────────────────────

def run():
    global TELEGRAM_CHAT_ID
    import config as _cfg

    if not TELEGRAM_BOT_TOKEN:
        print("ERROR: Set TELEGRAM_BOT_TOKEN in config.py")
        sys.exit(1)
    if not WAVESPEED_API_KEY:
        print("ERROR: Set WAVESPEED_API_KEY in config.py")
        sys.exit(1)

    if not TELEGRAM_CHAT_ID:
        print("[bot] No chat ID saved — send any message to your bot to register.")
    else:
        if _CLEAR_FLAG.exists():
            _clear_chat_history()
        send("🤖 Pipeline online. Send an Instagram URL or video file to start.")

    print("[bot] Polling Telegram...")
    _consecutive_errors = 0

    # Skip any pending updates so old messages aren't replayed on restart
    try:
        stale = requests.get(
            f"{TG_BASE}/getUpdates",
            params={"offset": -1, "timeout": 0},
            timeout=10,
        ).json().get("result", [])
        offset = (stale[-1]["update_id"] + 1) if stale else 0
        print(f"[bot] Starting at offset {offset}")
    except Exception:
        offset = 0

    while True:
        try:
            updates = get_updates(offset)
            if _consecutive_errors >= 5:
                send(f"⚡ Reconnected after {_consecutive_errors} errors.")
            _consecutive_errors = 0

            for upd in updates:
                offset = upd["update_id"] + 1

                # ── Inline button presses ─────────────────────────────────────
                if "callback_query" in upd:
                    cq      = upd["callback_query"]
                    cq_id   = cq["id"]
                    cq_data = cq.get("data", "")
                    cq_chat = str(cq.get("message", {}).get("chat", {}).get("id", ""))
                    try:
                        requests.post(f"{TG_BASE}/answerCallbackQuery",
                                      json={"callback_query_id": cq_id}, timeout=5)
                    except Exception:
                        pass
                    if cq_chat == str(TELEGRAM_CHAT_ID):
                        with _reply_lock:
                            rq = _reply_queue
                        if rq is not None:
                            if cq_data == "custom_prompt":
                                _tg("sendMessage",
                                    chat_id=TELEGRAM_CHAT_ID,
                                    text="✏️ Type your <b>additional prompt</b> — it will be layered on top of the default:",
                                    parse_mode="HTML",
                                    reply_markup={"force_reply": True,
                                                  "input_field_placeholder": "e.g. golden hour lighting, wearing sunglasses..."})
                            else:
                                rq.put(cq_data)
                    continue

                msg         = upd.get("message", {})
                incoming_id = str(msg.get("chat", {}).get("id", ""))
                if not incoming_id:
                    continue

                # Auto-register first sender and persist chat ID to config.py
                if not TELEGRAM_CHAT_ID:
                    TELEGRAM_CHAT_ID      = incoming_id
                    _cfg.TELEGRAM_CHAT_ID = incoming_id
                    print(f"[bot] Chat ID saved: {incoming_id}")
                    cfg_path = Path(__file__).parent / "config.py"
                    cfg_text = cfg_path.read_text()
                    cfg_text = re.sub(
                        r'TELEGRAM_CHAT_ID\s*=\s*""',
                        f'TELEGRAM_CHAT_ID   = "{incoming_id}"',
                        cfg_text,
                    )
                    cfg_path.write_text(cfg_text)
                    send(f"✅ Chat ID saved: {incoming_id}\n\n🤖 Pipeline online.\n\n" + _HELP_TEXT)
                    continue

                if incoming_id != str(TELEGRAM_CHAT_ID):
                    continue

                text = msg.get("text", "")
                if text:
                    _handle_message(text)
                    continue

                # Direct video/document upload
                video = msg.get("video") or msg.get("document")
                if video:
                    file_id   = video.get("file_id", "")
                    file_name = video.get("file_name", "") or video.get("file_unique_id", "video")
                    if file_id:
                        import uuid
                        dest = str(Path(TEMP_DIR) / f"{uuid.uuid4().hex[:8]}_{file_name}")
                        Path(TEMP_DIR).mkdir(exist_ok=True)
                        send("⬇️ Downloading your file...")
                        try:
                            download_tg_file(file_id, dest)
                            _executor.submit(_process_local_file, dest, file_name)
                        except Exception as e:
                            send(f"❌ File download failed: {e}")

        except KeyboardInterrupt:
            send("🛑 Pipeline shutting down.")
            break
        except Exception as e:
            err_str = str(e)
            is_transient = any(x in err_str.lower() for x in (
                "forcibly closed", "remotedisconnected", "connection reset",
                "read timeout", "connection aborted",
            ))
            if not is_transient:
                _consecutive_errors += 1
            print(f"[bot] poll {'drop' if is_transient else f'error #{_consecutive_errors}'}: {e}")
            if not is_transient and _consecutive_errors == 3:
                try:
                    send(f"⚠️ Bot struggling ({_consecutive_errors} errors): {err_str[:120]}")
                except Exception:
                    pass
            time.sleep(2 if is_transient else 5)


if __name__ == "__main__":
    run()

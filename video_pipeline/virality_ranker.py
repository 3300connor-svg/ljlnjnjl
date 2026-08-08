"""
virality_ranker.py — Score + rank a batch of videos by viral potential.

Uses Claude vision to score each video's thumbnail on:
  - emotional_intensity  (0-10) : raw emotion on face, expression power
  - controversy          (0-10) : provocative, edgy, debate-worthy content
  - visual_quality       (0-10) : sharpness, lighting, composition
  - viral_hook           (0-10) : pattern interrupt, scroll-stop power

Final score = weighted sum. Returns list sorted highest-first.
Requires ANTHROPIC_API_KEY in config.
"""

import base64
import json
import subprocess
import tempfile
from pathlib import Path

from config import ANTHROPIC_API_KEY


WEIGHTS = {
    "emotional_intensity": 0.30,
    "controversy":         0.30,
    "viral_hook":          0.25,
    "visual_quality":      0.15,
}

SCORE_PROMPT = """You are a social media virality analyst. You will score this video thumbnail.

Reply ONLY with valid JSON — no explanation, no markdown, nothing else:
{
  "emotional_intensity": <0-10>,
  "controversy":         <0-10>,
  "viral_hook":          <0-10>,
  "visual_quality":      <0-10>,
  "reasoning":           "<one sentence>"
}

Definitions:
- emotional_intensity: How much raw emotion or reaction the image evokes (shock, laughter, desire, anger)
- controversy: How provocative, edgy, or debate-worthy is the content
- viral_hook: Pattern interrupt power — would someone stop scrolling?
- visual_quality: Sharpness, lighting, framing quality
"""


def _extract_thumbnail(video_path: str) -> bytes:
    """Extract frame at 1s as JPEG bytes."""
    with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as tmp:
        tmp_path = tmp.name
    subprocess.run(
        [
            "ffmpeg", "-y",
            "-ss", "1",
            "-i", video_path,
            "-frames:v", "1",
            "-q:v", "2",
            tmp_path,
        ],
        check=True, capture_output=True,
    )
    data = Path(tmp_path).read_bytes()
    Path(tmp_path).unlink(missing_ok=True)
    return data


def _score_one(video_path: str) -> dict:
    """Score a single video. Returns scores dict + weighted total."""
    if not ANTHROPIC_API_KEY:
        return {"total": 0, "error": "no_api_key"}

    try:
        import anthropic
    except ImportError:
        return {"total": 0, "error": "anthropic_not_installed"}

    try:
        thumb = _extract_thumbnail(video_path)
    except Exception as e:
        return {"total": 0, "error": f"thumbnail_failed: {e}"}

    b64 = base64.standard_b64encode(thumb).decode()

    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
    try:
        resp = client.messages.create(
            model="claude-sonnet-5",
            max_tokens=256,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "image", "source": {"type": "base64", "media_type": "image/jpeg", "data": b64}},
                        {"type": "text",  "text": SCORE_PROMPT},
                    ],
                }
            ],
        )
        raw = resp.content[0].text.strip()
        scores = json.loads(raw)
        total = sum(scores.get(k, 0) * w for k, w in WEIGHTS.items())
        scores["total"] = round(total, 2)
        return scores
    except Exception as e:
        return {"total": 0, "error": str(e)}


def rank_videos(video_paths: list[str], progress_cb=None) -> list[dict]:
    """
    Score all videos and return them ranked highest virality first.

    Returns list of:
      {"rank": 1, "path": "...", "total": 8.3, "reasoning": "...", ...scores}
    """
    if progress_cb:
        progress_cb(f"Ranking {len(video_paths)} videos by virality...")

    scored = []
    for i, path in enumerate(video_paths):
        if progress_cb:
            progress_cb(f"  Scoring [{i+1}/{len(video_paths)}] {Path(path).name}")
        result = _score_one(path)
        result["path"] = path
        scored.append(result)

    scored.sort(key=lambda x: x.get("total", 0), reverse=True)
    for i, item in enumerate(scored):
        item["rank"] = i + 1

    return scored


def format_ranking(ranked: list[dict]) -> str:
    """Human-readable ranking summary for Telegram."""
    lines = ["Virality ranking:"]
    for item in ranked:
        name = Path(item["path"]).name
        total = item.get("total", "?")
        reason = item.get("reasoning", "")
        err = item.get("error", "")
        if err:
            lines.append(f"  #{item['rank']} {name} — scoring error: {err}")
        else:
            lines.append(f"  #{item['rank']} {name} — {total}/10  {reason}")
    return "\n".join(lines)

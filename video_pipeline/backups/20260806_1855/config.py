# ── CREDENTIALS ────────────────────────────────────────────────────────────────
TELEGRAM_BOT_TOKEN = "8925554170:AAGbmKdgK-5MVEdck3V4cPUSTVKtN_MjfL0"
TELEGRAM_CHAT_ID   = "8941578837"           # auto-saved on first message
WAVESPEED_API_KEY  = "wsk_live_wzmc6Kqahau6UhI41r6vBDHLrGO9A7n2Xzq0Y0kuuUM"
ANTHROPIC_API_KEY  = ""           # Claude API key — for virality scoring (optional)

# ── REFERENCE IMAGES (ibb.co — confirmed accessible by WaveSpeed) ─────────────
FACE_REFERENCE_URL = "https://i.ibb.co/sJd2qVsL/new-project.png"
BODY_REFERENCE_URL = "https://i.ibb.co/VcfhVwJB/4fac0d4a-932b-4455-8640-c232d5e7f739.jpg"

# ── SEEDREAM IMAGE PROMPT ──────────────────────────────────────────────────────
DEFAULT_IMAGE_PROMPT = (
    "Keep the scene exactly as-is — same pose, same background, same lighting, same clothing "
    "unless specified otherwise. Replace the subject's face and hair with the person from image two. "
    "Transplant image two's youthful, slim, feminine facial features, her natural light blue-green eyes, "
    "deep tanned skin tone including natural blemishes and freckles, and expression to image one. "
    "For hair: match the reference hair color, style, texture, but keep the hair positioning and length. "
    "Hair highlights must be natural sun-kissed balayage blended evenly throughout — NOT a single streak "
    "or panel on one side. Photorealistic, no artifacts, no halo, clean hairline and scalp. "
    "Authentic iPhone photo quality. Vertical 9:16 framing. No AI skin. No skin filters or makeup."
)

DEFAULT_KLING_PROMPT = (
    "Natural paced, smooth fluid movement. Preserve the subject's authentic motion and gestures "
    "from the original video. Seamless, cinematic quality. No jitter, no artifacts."
)

# ── WAVESPEED MODELS ───────────────────────────────────────────────────────────
WAVESPEED_BASE     = "https://api.wavespeed.ai"
SEEDREAM_MODEL     = "bytedance/seedream-v4.5/edit"
KLING_MODEL        = "kwaivgi/kling-v3.0-std/motion-control"

# ── KLING PRICING TABLE (seconds → USD) ───────────────────────────────────────
KLING_PRICING = {3: 0.378, 5: 0.63, 10: 1.26, 30: 3.78}

# ── DIRECTORIES ────────────────────────────────────────────────────────────────
OUTPUT_DIR          = "outputs/videos"
TRENDING_AUDIO_DIR  = "trending_audio"
TEMP_DIR            = "temp"

# ── VIDEO SETTINGS ─────────────────────────────────────────────────────────────
MAX_VIDEO_SECONDS   = 30          # trim input video if longer

# ── AUDIO / VIDEO ENCODE SETTINGS ─────────────────────────────────────────────
AUDIO_VOLUME  = 0.80
VIDEO_VOLUME  = 0.20
VIDEO_CODEC   = "libx264"
AUDIO_CODEC   = "aac"
CRF           = 23
OUTPUT_FORMAT = "mp4"

# ── BULK BATCH SETTINGS ───────────────────────────────────────────────────────
BULK_COLLECT_WINDOW = 12   # seconds to wait for more links before starting batch

# ── FALLBACK URLS (opened in browser when an API fails) ───────────────────────
FALLBACK_URLS = {
    "fastdl":    "https://fastdl.app/en4",
    "catbox":    "https://catbox.moe/",
    "seedream":  "https://wavespeed.ai/models/bytedance/seedream-v4.5/edit",
    "kling":     "https://wavespeed.ai/models/kwaivgi/kling-v3.0-std/motion-control",
}

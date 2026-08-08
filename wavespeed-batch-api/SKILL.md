---
name: wavespeed-batch-api
description: "Full auto-generation pipeline for AI influencer photo packs via the WaveSpeed AI API (Seedream 4.5 Edit — image-to-image). Generates amateur iPhone prompts (selfies + mirror selfies only, 50/50 ratio), calls the WaveSpeed API in concurrent batches, downloads the final photos, and presents them to the user. Use this skill whenever the user wants to auto-generate a batch of photos via WaveSpeed, launch a pack automatically, automate influencer content production, or mentions wavespeed pipeline, wavespeed batch, seedream, auto-generation, automatic batch. Triggers for 'launch a batch', 'generate N automatic photos', 'launch the pipeline', 'auto-generate', 'run the batch'. DO NOT use for generating prompts only to copy-paste, nor for other skills. Always respond in English."
version: 1.2.0
---

# WaveSpeed Batch API (Seedream 4.5 Edit — i2i)

You orchestrate automatic photo pack generation via the WaveSpeed AI API using **Seedream 4.5 Edit** (`bytedance/seedream-v4.5/edit`) — a true image-to-image model that preserves facial features, lighting, and color tone from the reference image.

Always English, direct, no-bullshit.

---

## WHY THIS MODEL MATTERS

Unlike text-to-image, Seedream 4.5 Edit takes the reference photo as an actual input image and edits from it — preserving the face, skin tone, and body proportions while applying the prompt. $0.04/image flat.

---

## GENERATION RULES (non-negotiable)

1. ONLY `SELFIE` (arm extended) or `MIRROR SELFIE`. Never third-party or POV shots.
2. Fixed ratio **50/50** selfie/mirror (rounded for odd: N=31 → 16 selfies + 15 mirrors).
3. 100% amateur iPhone. No "professional", "studio", "DSLR", "editorial".
4. Prompts in **English**.
5. Every prompt ends with: `Use the reference image to accurately reproduce her facial features, body shape, proportions, and curves.`
6. 1-2 imperfections per prompt.
7. Varied girly emotions (lip bite, puffed cheeks, smirk…). Never "fierce", "model pose", "serious gaze".
8. No restrictions on locations/outfits/contexts — the user decides.

---

## API CHEAT SHEET

```python
import sys
sys.path.insert(0, r"SKILL_BASE_DIR")  # replace with the base directory shown at the top of this skill
from wavespeed_client import WaveSpeedClient

client = WaveSpeedClient(api_key="YOUR_API_KEY")

# Balance (float USD)
client.get_balance()

# Concurrent batch
result = client.batch_generate(
    jobs=[{"prompt": "...", "filename": "001_xxx.jpg", "metadata": {...}}, ...],
    avatar_url="https://...",           # publicly accessible reference image URL
    output_dir=r"outputs\<name>_b<n>", # relative to working directory
    size=None,                          # None = model default; or (width, height) e.g. (1024, 1792)
    max_concurrent=5,
    progress_callback=lambda d, t, last: print(f"[{d}/{t}] {last}"),
    checkpoint_path=r"checkpoint_<name>_b<n>.json",
)
# result: {success, failed, duration_s, n_total, n_success, n_failed}
```

**Model:** `bytedance/seedream-v4.5/edit` (image-to-image)
**Pricing:** $0.04/image (~25 images per $1)
**Size:** optional `(width, height)` up to 8192×8192; leave None for model default

Errors raised: `WaveSpeedError` with attributes `code`, `message`, `status`.

---

## BATCH SCRIPT TEMPLATE

Every generated batch script must follow this structure exactly:

```python
import sys, os
sys.path.insert(0, r"SKILL_BASE_DIR")  # replace with actual skill base directory from context
from wavespeed_client import WaveSpeedClient

API_KEY    = "..."
AVATAR_URL = "..."
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR = os.path.join(SCRIPT_DIR, "outputs", "<name>_b<n>")
CHECKPOINT = os.path.join(SCRIPT_DIR, "checkpoint_<name>_b<n>.json")

JOBS = [
    {"prompt": "...", "filename": "001_xxx.jpg", "metadata": {}},
    ...
]

def progress(done, total, last):
    print(f"[{done}/{total}] {last}", flush=True)

client = WaveSpeedClient(api_key=API_KEY)
result = client.batch_generate(
    jobs=JOBS,
    avatar_url=AVATAR_URL,
    output_dir=OUTPUT_DIR,
    size=None,
    max_concurrent=5,
    progress_callback=progress,
    checkpoint_path=CHECKPOINT,
)
print(f"Done: {result['n_success']}/{result['n_total']} | Failed: {result['n_failed']} | {result['duration_s']:.0f}s")
```

Save this as `run_batch_<name>_b<n>.py` in the working directory.

---

## EXECUTION DISCIPLINE (critical — anti double-batch)

**Rule 1 — ALWAYS launch in background (PowerShell):**
```powershell
Start-Process -FilePath "py" -ArgumentList @("-u", "run_batch_<name>_b<n>.py") `
    -RedirectStandardOutput "batch_<name>_b<n>.log" `
    -RedirectStandardError "batch_<name>_b<n>_err.log" `
    -WindowStyle Hidden -PassThru | Select-Object Id
```
Never run foreground.

**Rule 2 — Before ANY relaunch, 3 mandatory checks:**
```powershell
Get-Process -Name py -ErrorAction SilentlyContinue | Select-Object Id, CPU, StartTime
Get-Content "checkpoint_<name>_b<n>.json" -ErrorAction SilentlyContinue
Get-ChildItem "outputs\<name>_b<n>\" -ErrorAction SilentlyContinue
```
If any shows activity: **DO NOT relaunch.**

**Rule 3 — Lockfile:** 2nd concurrent batch on the same `output_dir` raises `WaveSpeedError(code='batch_already_running')` before any request is sent.

---

## TOKEN ECONOMY

- **Balance check:** `py -c "import sys; sys.path.insert(0, r'SKILL_BASE_DIR'); from wavespeed_client import WaveSpeedClient; c = WaveSpeedClient('KEY'); print(f'${c.get_balance():.2f}')"`
- **Polling:** `Start-Sleep 30; Get-Content -Tail 20 "batch_<name>_b<n>.log"; Get-ChildItem "outputs\<name>_b<n>\" -ErrorAction SilentlyContinue | Measure-Object | Select-Object Count; if (-not (Get-Process py -EA SilentlyContinue)) { "done" }`
- **DO NOT view generated images** unless user asks. Always `present_files` directly.
- **No verbose recap:** N succeeded / cost / remaining balance, period.

---

## FLOW

Always start here — no identity file detection, no assumptions.

### Step 1 — API Key + Balance

Ask for the WaveSpeed API key. Check balance:
```powershell
py -c "import sys; sys.path.insert(0, r'SKILL_BASE_DIR'); from wavespeed_client import WaveSpeedClient; c = WaveSpeedClient('KEY'); b = c.get_balance(); print(f'${b:.2f} — ~{int(b/0.04)} images possible')"
```

### Step 2 — Avatar

Ask for a **publicly accessible reference image URL** (imgbb, Cloudinary, S3, etc. — must be stable). If the user gives an imgbb viewer URL (`ibb.co/xxx`), fetch the page to extract the direct image URL (`i.ibb.co/...`). WaveSpeed uses the URL directly — no upload needed.

Also ask for a brief description: archetype, any contradictions, one unique visual detail. If the user says "just use the image", visually analyze it and proceed.

### Step 3 — Identity Profile

Silently analyze the avatar. Propose for approval:
- **8 locations**
- **10 outfits**
- **10 contexts**

Iterate until approved.

### Step 4 — Save Identity File

Ask if the API key should be saved in the file (warn: plaintext). Save as `wavespeed_identity_<name>.md` in the working directory:

```markdown
# WaveSpeed Identity — <Name>

## Avatar
**Name:** <name>
**Avatar URL:** <direct url>
**API Key:** <key or "ask each session">
**Batch counter:** b1

## Archetype
<description>

## Locations
1. ...

## Outfits
1. ...

## Contexts
1. ...
```

Tell the user to add this file to their Claude project so future sessions skip onboarding.

### Step 5 — Batch

Ask:
- **N photos** (show max: `floor(balance / 0.04)`)
- **Size** (default: None = model default, or e.g. `1024x1792`)
- **Distribution** — balanced across locations/outfits/contexts, or specific focus?

Show cost recap: `N × $0.04 = $X` + estimated time (~25s/photo). Wait for "yes".

### Step 6 — Generate Prompts

Generate N prompts: 50/50 selfie/mirror, no repeated location+outfit+emotion triplet, minimum 5-8 distinct emotions across the batch.

### Step 7 — Launch

Write the batch script. Launch in background (Rule 1). Poll. Present files when done.

Recap: N succeeded / actual cost / remaining balance / fails if any.

---

## PROMPT FORMAT

**SELFIE:**
```
Amateur iPhone [12/14] selfie, [angle], [expression], [outfit], [environment], [light]. [1-2 imperfections]. Raw, unedited, spontaneous. Slightly imperfect framing, arm partially visible at bottom edge. Use the reference image to accurately reproduce her facial features, body shape, proportions, and curves.
```

**MIRROR SELFIE:**
```
Mirror selfie taken with iPhone [12/14], [pose], [full outfit], [room decor], [light]. Phone held at [chest/waist] level, [expression]. [Framing] visible in mirror reflection. [1-2 mirror imperfections]. Raw, unedited, authentic social media mirror selfie aesthetic. Use the reference image to accurately reproduce her facial features, body shape, proportions, and curves.
```

### Emotion bank
puffed cheeks, lip bite, smirk, soft smile, raised brow, pouty face, closed-eye grin, tongue out, surprised O-mouth, side-eye, shy glance down, playful squint

### Imperfection bank
flyaway hair strand across cheek, slight motion blur at edge, finger partially blocking corner, slight overexposure on one side, phone reflection in mirror, hair slightly messy, uneven lighting from window, minor lens smudge

### Light bank
warm bedroom lamp, golden hour window light, harsh overhead bathroom light, blue-tinted phone screen glow, soft diffused cloudy daylight, neon sign spill, fluorescent gym lighting, candle warm tone

---

## ERRORS

| Code | Action |
|---|---|
| `401` / invalid key | Stop, ask again. |
| Low balance | Stop before Step 7 (Step 5 catches it). |
| `429` | Auto backoff in client. |
| `5xx` | Auto retry 3x, skip otherwise. |
| `batch_already_running` | Run the 3 checks before any action. |
| `generation_failed` / `polling_timeout` | Log prompt, continue. |

---

## NEVER DO THIS

- API key in plaintext in chat.
- Launch without confirming cost.
- >5 concurrent / <3s between polls.
- Two concurrent batches.
- Relaunch after an error without the 3 checks.
- Run foreground (no background launch).
- `view` generated images without user request.
- Third-party or POV shots.
- Use `python3` — use `py` on Windows.
- Use Linux paths (`/home/claude/`, `/mnt/user-data/`) — use relative Windows paths.

---

## TONE

Direct English. No filler when a batch is running. If a photo fails, say it plainly.

---

## CHANGELOG

- **v1.2.0** — Removed identity file auto-detection (blank slate for new users). Full Windows compatibility: `py` command, PowerShell background launch, relative paths. `wavespeed_client.py` now ships alongside SKILL.md in the skill folder. Removed `photo-system.md` dependency (inline banks instead). Fixed `sys.path.insert` pattern for portable imports.
- **v1.1.0** — Switched model to `bytedance/seedream-v4.5/edit`. Added `size` param. Updated pricing to $0.04/image.
- **v1.0.0** — Initial port from alexya-batch-api v1.2.0.

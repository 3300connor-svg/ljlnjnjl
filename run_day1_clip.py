import os, time, random, requests

API_KEY   = "wsk_live_MWD0E5QYAIV4CP2S3ya2QPZvTApxlw8oBSqPaeLIZ-E"
BASE_URL  = "https://api.wavespeed.ai/api/v3"
VID_MODEL = "bytedance/seedance-2.0/image-to-video"

# ── paste your imgbb (or any hosted) URLs here ──────────────────────
START_FRAME = ""  # her back to camera, arranging pillow, dark, night
END_FRAME   = ""  # her turned, looking back at camera, same angle
# ────────────────────────────────────────────────────────────────────

OUTPUT_DIR = r"C:\Users\pheno\Downloads\wavespeed-batch-api\outputs\day1"
os.makedirs(OUTPUT_DIR, exist_ok=True)
OUT_PATH   = os.path.join(OUTPUT_DIR, "day1_arrival.mp4")

headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json",
}

PROMPT = (
    "She slowly smooths the sheet with one tired hand, arranging the pillow. "
    "Heavy movements, half asleep, not looking at what she is doing. "
    "The goldendoodle turns and stares directly at the camera — ears up, completely still. "
    "She feels it. Glances down at the dog. Follows its eyeline slowly over her left shoulder. "
    "Finds the camera. Hair falls forward with the turn. She holds the look — "
    "tired, unreadable, not performing. Just caught. "
    "Camera completely static. Does not move at any point. "
    "Everything before the turn is slow and heavy. The turn takes one full second. "
    "The hold is the last half second before cut."
)

if not START_FRAME or not END_FRAME:
    print("ERROR: paste START_FRAME and END_FRAME URLs before running.")
    exit(1)

print("Submitting Day 1 — Arrival to Seedance 2.0...")
print(f"  Resolution: 1080p | Duration: 5s | 9:16 | no audio")

resp = requests.post(
    f"{BASE_URL}/{VID_MODEL}",
    headers=headers,
    json={
        "image":        START_FRAME,
        "last_image":   END_FRAME,
        "prompt":       PROMPT,
        "resolution":   "1080p",
        "duration":     5,
        "aspect_ratio": "9:16",
        "generate_audio": False,
    },
    timeout=30,
)

if resp.status_code != 200:
    print(f"Submit failed {resp.status_code}: {resp.text}")
    exit(1)

task_id = resp.json()["data"]["id"]
print(f"Task ID: {task_id} — polling...")

deadline = time.time() + 600
while time.time() < deadline:
    r = requests.get(
        f"{BASE_URL}/predictions/{task_id}/result",
        headers=headers,
        timeout=30,
    )
    data   = r.json().get("data", {})
    status = data.get("status")
    print(f"  [{status}]")
    if status == "completed":
        video_url = data["outputs"][0]
        print(f"Rendered: {video_url}")
        dl = requests.get(video_url, timeout=300, stream=True)
        dl.raise_for_status()
        with open(OUT_PATH, "wb") as f:
            for chunk in dl.iter_content(65536):
                f.write(chunk)
        print(f"Saved: {OUT_PATH}")
        break
    if status == "failed":
        print(f"Failed: {data.get('error')}")
        break
    time.sleep(10 + random.uniform(0, 3))

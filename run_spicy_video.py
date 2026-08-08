import os, time, random, requests

API_KEY    = "wsk_live_MWD0E5QYAIV4CP2S3ya2QPZvTApxlw8oBSqPaeLIZ-E"
MODEL      = "wavespeed-ai/wan-2.2-spicy/image-to-video"
BASE_URL   = "https://api.wavespeed.ai/api/v3"
START_IMG  = "https://i.ibb.co/8gd2SqKH/download.jpg"
OUTPUT     = r"C:\Users\pheno\Downloads\wavespeed-batch-api\outputs\spicy_video\blacks_beach_pov_avatar.mp4"

os.makedirs(os.path.dirname(OUTPUT), exist_ok=True)

headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json",
}

PROMPT = (
    "POV video at Black's Beach San Diego, sunny afternoon, nude girl standing in front of camera at the water's edge, "
    "looking directly at the viewer with a natural flirty expression, wet hair, water droplets on her golden skin. "
    "She slowly moves closer toward the camera, body fully visible, breasts moving naturally. "
    "Torrey Pines sandstone cliffs in background, real natural coastal light, ocean waves behind her. "
    "Candid, unfiltered, amateur handheld POV feel. No music, no text overlays."
)

print(f"Submitting to {MODEL}...")
resp = requests.post(
    f"{BASE_URL}/{MODEL}",
    headers=headers,
    json={
        "image": START_IMG,
        "prompt": PROMPT,
        "resolution": "720p",
        "duration": 5,
        "seed": -1,
    },
    timeout=30,
)
resp.raise_for_status()
task_id = resp.json()["data"]["id"]
print(f"Task ID: {task_id} — polling...")

deadline = time.time() + 600
while time.time() < deadline:
    r = requests.get(f"{BASE_URL}/predictions/{task_id}/result", headers=headers, timeout=30)
    data = r.json().get("data", {})
    status = data.get("status")
    print(f"  status: {status}")
    if status == "completed":
        url = data["outputs"][0]
        print(f"Done! Downloading from {url}")
        vid = requests.get(url, timeout=300, stream=True)
        vid.raise_for_status()
        with open(OUTPUT, "wb") as f:
            for chunk in vid.iter_content(65536):
                f.write(chunk)
        print(f"Saved: {OUTPUT}")
        break
    if status == "failed":
        print(f"FAILED: {data.get('error')}")
        break
    time.sleep(8 + random.uniform(0, 2))

import sys, os, time, random, requests
sys.path.insert(0, r"C:\Users\pheno\Downloads\wavespeed-batch-api\wavespeed-batch-api")

API_KEY    = "wsk_live_MWD0E5QYAIV4CP2S3ya2QPZvTApxlw8oBSqPaeLIZ-E"
AVATAR_URL = "https://i.ibb.co/8gd2SqKH/download.jpg"
MODEL      = "wavespeed-ai/flux-2-dev/edit"
BASE_URL   = "https://api.wavespeed.ai/api/v3"
OUTPUT     = r"C:\Users\pheno\Downloads\wavespeed-batch-api\outputs\flux_test\flux_test_bend.jpg"

os.makedirs(os.path.dirname(OUTPUT), exist_ok=True)

headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json",
}

PROMPT = (
    "Candid photo shot from directly behind, close up, low camera angle at Black's Beach San Diego. "
    "Girl completely nude, bent fully forward at the waist, legs planted wide apart, both hands reaching down to grab her surfboard off the sand. "
    "Camera tight and close behind her, framing her ass and full anatomy between her legs prominently. "
    "Head down, wet salty hair hanging forward — not looking at camera at all, back of head only. "
    "Wide bent-over stance with legs apart, full vulva and anatomy exposed naturally from this direct behind angle. "
    "Torrey Pines sandstone cliffs in background. "
    "Direct afternoon coastal sun casting hard natural shadows across her body, deep defined shadow contrast, "
    "uneven light, hot spots on skin, imperfect exposure. Sharp image, crisp natural skin texture, no blur. "
    "Golden sun-kissed Brazilian complexion, lighter warm skin. Youthful 19-21 body. "
    "Thick toned legs, round prominent ass. Unposed, genuinely caught mid-action."
)

print("Submitting to FLUX 2 Dev...")
resp = requests.post(
    f"{BASE_URL}/{MODEL}",
    headers=headers,
    json={
        "images": [AVATAR_URL],
        "prompt": PROMPT,
        "size": "1024*1792",
        "enable_sync_mode": False,
        "enable_base64_output": False,
    },
    timeout=30,
)
resp.raise_for_status()
task_id = resp.json()["data"]["id"]
print(f"Task ID: {task_id} — polling...")

deadline = time.time() + 300
while time.time() < deadline:
    r = requests.get(f"{BASE_URL}/predictions/{task_id}/result", headers=headers, timeout=30)
    data = r.json().get("data", {})
    status = data.get("status")
    print(f"  status: {status}")
    if status == "completed":
        url = data["outputs"][0]
        print(f"Done! Downloading from {url}")
        img = requests.get(url, timeout=120, stream=True)
        img.raise_for_status()
        with open(OUTPUT, "wb") as f:
            for chunk in img.iter_content(8192):
                f.write(chunk)
        print(f"Saved: {OUTPUT}")
        break
    if status == "failed":
        print(f"FAILED: {data.get('error')}")
        break
    time.sleep(5 + random.uniform(0, 1))

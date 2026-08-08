import os, time, random, requests

API_KEY    = "wsk_live_MWD0E5QYAIV4CP2S3ya2QPZvTApxlw8oBSqPaeLIZ-E"
BASE_URL   = "https://api.wavespeed.ai/api/v3"
REF_IMAGE  = "https://i.ibb.co/CrLVzrr/image.png"   # body/scene
FACE_IMAGE = "https://i.ibb.co/8gd2SqKH/download.jpg"  # Nova avatar face
OUT_SWAP   = r"C:\Users\pheno\Downloads\wavespeed-batch-api\outputs\spicy_video\faceswap_frame.jpg"
OUT_VIDEO  = r"C:\Users\pheno\Downloads\wavespeed-batch-api\outputs\spicy_video\blacks_beach_faceswap.mp4"

os.makedirs(os.path.dirname(OUT_SWAP), exist_ok=True)

headers = {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}

def poll(task_id, timeout=300):
    deadline = time.time() + timeout
    while time.time() < deadline:
        r = requests.get(f"{BASE_URL}/predictions/{task_id}/result", headers=headers, timeout=30)
        data = r.json().get("data", {})
        status = data.get("status")
        print(f"  [{status}]")
        if status == "completed":
            return data["outputs"][0]
        if status == "failed":
            raise RuntimeError(f"Failed: {data.get('error')}")
        time.sleep(5 + random.uniform(0, 1))
    raise RuntimeError("Timeout")

def download(url, path, chunk=65536):
    r = requests.get(url, timeout=300, stream=True)
    r.raise_for_status()
    with open(path, "wb") as f:
        for chunk_data in r.iter_content(chunk):
            f.write(chunk_data)
    print(f"Saved: {path}")
    return path

# Step 1 — Face swap
print("Step 1: Face swap ($0.025)...")
resp = requests.post(f"{BASE_URL}/wavespeed-ai/image-face-swap-pro", headers=headers, json={
    "image": REF_IMAGE,
    "face_image": FACE_IMAGE,
    "output_format": "jpeg",
}, timeout=30)
resp.raise_for_status()
task_id = resp.json()["data"]["id"]
print(f"Task: {task_id}")
swapped_url = poll(task_id)
print(f"Swapped frame: {swapped_url}")
download(swapped_url, OUT_SWAP)

# Step 2 — Animate with spicy video model
print("\nStep 2: Animate spicy video ($0.30)...")
PROMPT = (
    "POV video at Black's Beach San Diego, sunny afternoon, nude girl standing at the water's edge "
    "looking directly at the viewer with a natural flirty expression, wet hair, water droplets on golden skin. "
    "She slowly moves closer toward camera, body fully visible, natural movement. "
    "Torrey Pines sandstone cliffs in background, real coastal light, ocean waves behind her. "
    "Candid, unfiltered, amateur handheld POV feel."
)
resp = requests.post(f"{BASE_URL}/wavespeed-ai/wan-2.2-spicy/image-to-video", headers=headers, json={
    "image": swapped_url,
    "prompt": PROMPT,
    "resolution": "720p",
    "duration": 5,
    "seed": -1,
}, timeout=30)
resp.raise_for_status()
task_id = resp.json()["data"]["id"]
print(f"Task: {task_id}")
video_url = poll(task_id, timeout=600)
print(f"Video: {video_url}")
download(video_url, OUT_VIDEO)

print("\nAll done.")

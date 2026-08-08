import os, time, random, requests

API_KEY    = "wsk_live_MWD0E5QYAIV4CP2S3ya2QPZvTApxlw8oBSqPaeLIZ-E"
MODEL      = "openai/gpt-image-2/edit"
BASE_URL   = "https://api.wavespeed.ai/api/v3"
AVATAR_URL = "https://i.ibb.co/8gd2SqKH/download.jpg"
BIKINI_REF = "https://i.ibb.co/BKBjtsn4/004-blacks-beach-bikini-v3.jpg"
OUTPUT     = r"C:\Users\pheno\Downloads\wavespeed-batch-api\outputs\gpt_test\bikini_2k_high.jpg"

os.makedirs(os.path.dirname(OUTPUT), exist_ok=True)

headers = {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}

PROMPT = (
    "Candid photo at Black's Beach La Jolla San Diego, late afternoon. "
    "Girl standing near the water wearing a black string bikini, wet hair stuck to her face and neck, "
    "small water droplets on her golden skin. Close personal framing showing her full figure. "
    "Tall sandstone Torrey Pines cliffs in the background. "
    "Flat natural ambient coastal daylight — real unfiltered outdoor afternoon light, slight warmth, no dramatic highlights, "
    "no glowing skin, no cinematic lighting. Slightly noisy exposure, muted color tones, natural skin texture. "
    "Unposed, caught off guard, genuinely in the moment. "
    "Golden sun-kissed Brazilian complexion, lighter warm skin. Natural blue eyes with green center. "
    "Sun-kissed brunette hair with natural blonde highlights. Soft light freckles across nose and cheeks. "
    "Youthful 19-21, surfer girl, coastal San Diego. Thick toned legs, round ass, generous chest. "
    "Use the reference images to accurately reproduce her face, body shape, and proportions."
)

print(f"Submitting to GPT Image 2 — high quality, 2K ($0.44)...")
resp = requests.post(
    f"{BASE_URL}/{MODEL}",
    headers=headers,
    json={
        "images": [AVATAR_URL, BIKINI_REF],
        "prompt": PROMPT,
        "quality": "high",
        "resolution": "2k",
        "aspect_ratio": "9:16",
        "output_format": "jpeg",
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
    print(f"  [{status}]")
    if status == "completed":
        url = data["outputs"][0]
        print(f"Done! {url}")
        img = requests.get(url, timeout=300, stream=True)
        img.raise_for_status()
        with open(OUTPUT, "wb") as f:
            for chunk in img.iter_content(65536):
                f.write(chunk)
        print(f"Saved: {OUTPUT}")
        break
    if status == "failed":
        print(f"FAILED: {data.get('error')}")
        break
    time.sleep(6 + random.uniform(0, 1))

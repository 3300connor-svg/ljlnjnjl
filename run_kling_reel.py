import os, time, random, requests
from concurrent.futures import ThreadPoolExecutor, as_completed

API_KEY    = "wsk_live_MWD0E5QYAIV4CP2S3ya2QPZvTApxlw8oBSqPaeLIZ-E"
MODEL      = "kwaivgi/kling-v3-turbo-pro/image-to-video"
BASE_URL   = "https://api.wavespeed.ai/api/v3"
AVATAR_URL  = "https://i.ibb.co/8gd2SqKH/download.jpg"           # face/identity — interior scenes
BIKINI_REF  = "https://i.ibb.co/PvfKWTG5/004-blacks-beach-bikini-v3.jpg"  # beach environment
NUDE_REF    = "https://i.ibb.co/FLg4n2mL/004-blacks-beach-nude-v3.jpg"    # beach at water
SIDELAY_REF = "https://i.ibb.co/PGFb30dh/005-blacks-beach-side-lay.jpg"   # beach body/sand
OUTPUT_DIR  = r"C:\Users\pheno\Downloads\wavespeed-batch-api\outputs\kling_reel"
DURATION    = "3"  # 3s per clip = $0.42/clip

os.makedirs(OUTPUT_DIR, exist_ok=True)

headers = {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}

UNIVERSAL = (
    "Golden sun-kissed Brazilian complexion. Natural blue-green eyes. "
    "Sun-kissed brunette hair with blonde highlights. Soft freckles. "
    "Youthful 19-21 surfer girl. Natural ambient light, iPhone quality, candid, unposed."
)

SCENES = [
    {
        "filename": "01_hook_bronco_interior.mp4",
        "prompt": f"Inside a yellow Ford Bronco, early morning, windows fogged up, warm sunrise light through the glass. Girl in oversized faded hoodie, bare legs, wet messy hair, sitting in the passenger seat looking tired and intimate. Dog shifts in the back seat. Slightly underexposed, warm muted tones. She wipes a small circle in the fogged window with her hand. {UNIVERSAL}",
    },
    {
        "filename": "02_coffee_hood.mp4",
        "prompt": f"Back of girl to camera, standing at the hood of a yellow Ford Bronco parked at Black's Beach San Diego, both hands wrapped around a thermos cup. Oversized faded hoodie, bare legs below the hem, wet hair down her back. Ocean and morning coastal haze behind her. She slowly breathes steam rising from the cup. Natural flat ambient morning light, muted warm tones. {UNIVERSAL}",
    },
    {
        "filename": "03_cliff_trail.mp4",
        "prompt": f"Back of girl to camera walking up a sandy cliff trail at Black's Beach La Jolla San Diego, surfboard under one arm. Oversized hoodie, bare legs, wet hair stuck to her back. Low morning sun. Torrey Pines sandstone cliffs visible. She walks slowly, tired, unhurried. Slight handheld camera sway. Natural light, muted tones. {UNIVERSAL}",
    },
    {
        "filename": "04_waters_edge.mp4",
        "prompt": f"Back of girl to camera standing at the water's edge at Black's Beach San Diego, just got out of the ocean. Oversized hoodie wet at hem, bare legs, wet hair on her back. She stands still looking out at the ocean, small waves washing over her feet. Flat coastal morning light, muted blue-grey tones. {UNIVERSAL}",
    },
    {
        "filename": "05_outdoor_rinse.mp4",
        "prompt": f"Back of girl to camera at an outdoor beach rinse shower at Black's Beach parking lot, water running over her wet hair down her back. Oversized hoodie, bare legs, eyes closed. Yellow Ford Bronco visible in background. Water streams down slowly. Natural daylight, slightly overexposed where water catches light. {UNIVERSAL}",
    },
    {
        "filename": "06_bronco_interior_dog.mp4",
        "prompt": f"Inside yellow Ford Bronco, girl folding a blanket in the back seat, dog circling around her feet. Oversized hoodie, bare legs, damp hair. Interior lived-in but neat. She moves slowly and tiredly. Warm dim interior light, slightly underexposed, natural shadows. {UNIVERSAL}",
    },
    {
        "filename": "07_driver_seat_eyes_closed.mp4",
        "prompt": f"Girl in the driver's seat of a yellow Ford Bronco, head leaned back against the headrest, eyes closed, one hand resting on the steering wheel. Oversized hoodie, bare legs. Morning light through the windshield on her face. She breathes slowly and peacefully. Natural light, muted warm tones. {UNIVERSAL}",
    },
    {
        "filename": "08_trigger_looks_at_camera.mp4",
        "prompt": f"Girl in the driver's seat of a yellow Ford Bronco looking directly at the camera, tired natural expression, slightly intimate. Oversized hoodie, wet hair half-dry. Morning light through windshield. Direct eye contact, not posing — caught in a real moment. She blinks slowly and looks out the window. Muted warm tones, natural light. {UNIVERSAL}",
    },
    {
        "filename": "09_reaction_ring_light.mp4",
        "prompt": f"Girl inside yellow Ford Bronco fixing her hair in the rearview mirror, ring light glowing softly on the dashboard. She pauses mid-motion and slowly turns toward camera realizing it's still recording. Small unreadable expression — not startled, just caught. She holds the look for a beat then slowly reaches toward the lens. Warm ring light glow mixing with dim interior. {UNIVERSAL}",
    },
]

def poll(task_id, timeout=600):
    deadline = time.time() + timeout
    while time.time() < deadline:
        r = requests.get(f"{BASE_URL}/predictions/{task_id}/result", headers=headers, timeout=30)
        data = r.json().get("data", {})
        status = data.get("status")
        if status == "completed":
            return data["outputs"][0]
        if status == "failed":
            raise RuntimeError(f"Failed: {data.get('error')}")
        time.sleep(8 + random.uniform(0, 2))
    raise RuntimeError("Timeout")

def generate_clip(scene):
    fname = scene["filename"]
    out_path = os.path.join(OUTPUT_DIR, fname)
    if os.path.exists(out_path):
        print(f"SKIP {fname} (exists)")
        return fname, True

    resp = requests.post(
        f"{BASE_URL}/{MODEL}",
        headers=headers,
        json={
            "image": AVATAR_URL,
            "prompt": scene["prompt"],
            "duration": DURATION,
        },
        timeout=30,
    )
    resp.raise_for_status()
    task_id = resp.json()["data"]["id"]
    print(f"  [{fname}] task: {task_id}")

    url = poll(task_id)
    r = requests.get(url, timeout=300, stream=True)
    r.raise_for_status()
    with open(out_path, "wb") as f:
        for chunk in r.iter_content(65536):
            f.write(chunk)
    print(f"  DONE {fname}")
    return fname, True

print(f"Launching {len(SCENES)} Kling clips | {DURATION}s each | ~${0.14 * int(DURATION) * len(SCENES):.2f} total")

with ThreadPoolExecutor(max_workers=3) as pool:
    futures = {pool.submit(generate_clip, s): s for s in SCENES}
    for fut in as_completed(futures):
        try:
            fname, ok = fut.result()
            print(f"[COMPLETE] {fname}")
        except Exception as e:
            print(f"[ERROR] {futures[fut]['filename']}: {e}")

print(f"\nAll clips saved to: {OUTPUT_DIR}")
print("Stitch order: 01 → 02 → 03 → 04 → 05 → 06 → 07 → 08 → 09")

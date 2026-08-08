import os, time, random, requests
from concurrent.futures import ThreadPoolExecutor, as_completed

API_KEY   = "wsk_live_MWD0E5QYAIV4CP2S3ya2QPZvTApxlw8oBSqPaeLIZ-E"
BASE_URL  = "https://api.wavespeed.ai/api/v3"
IMG_MODEL = "bytedance/seedream-v4.5/edit"
VID_MODEL = "bytedance/seedance-2.0/image-to-video"

OUTPUT_DIR = r"C:\Users\pheno\Downloads\wavespeed-batch-api\outputs\seedance_reel"
STILLS_DIR = os.path.join(OUTPUT_DIR, "stills")
CLIPS_DIR  = os.path.join(OUTPUT_DIR, "clips")

os.makedirs(STILLS_DIR, exist_ok=True)
os.makedirs(CLIPS_DIR, exist_ok=True)

# All 5 reference images — used by Seedream for every still
REFS = [
    "https://i.ibb.co/8gd2SqKH/download.jpg",                        # avatar / face
    "https://i.ibb.co/PvfKWTG5/004-blacks-beach-bikini-v3.jpg",      # bikini beach
    "https://i.ibb.co/FLg4n2mL/004-blacks-beach-nude-v3.jpg",        # nude beach
    "https://i.ibb.co/PGFb30dh/005-blacks-beach-side-lay.jpg",       # side lay
    "https://i.ibb.co/Y4TxnWnn/009-restaurant-night-coastal-edited.jpg",  # restaurant night
]

headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json",
}

UNIVERSAL = (
    "Golden sun-kissed Brazilian complexion, lighter warm skin tone. "
    "Natural blue-green eyes. Sun-kissed brunette hair with natural blonde highlights. "
    "Soft light freckles across nose and cheeks. Youthful 19-21 surfer girl, "
    "thick toned legs, generous chest in oversized faded vintage hoodie, bare legs below the hem. "
    "Shot on iPhone — candid, unposed, no studio lighting, no artificial glow, no flash. "
    "Natural ambient light only. Slight noise grain, natural skin texture, muted coastal tones. "
    "Lighting imperfections, directional shadows, not evenly lit. Real girl, real moment."
)

SCENES = [
    {
        "filename": "01_hook_bronco_interior",
        "still_prompt": (
            "Inside yellow Ford Bronco early morning, girl in oversized faded vintage hoodie, bare legs below the hem, "
            "wet messy hair loose. Sitting in the passenger seat facing the window. "
            "Dog shifting in the back cargo area. Windows fogged from her breath. "
            "Warm dim pre-sunrise amber light filtering through the fogged glass — soft, uneven, underexposed. "
            "Deep shadows on her face from the door pillar and headrest. Shadow falls under her chin and on the side away from the window. "
            "Tired intimate expression, looking out the fogged glass. No ring light, no flash. "
            "iPhone candid from low dashboard angle, slight lens imperfection. Warm amber interior, visible grain. "
            + UNIVERSAL
        ),
        "motion_prompt": (
            "Dog shifts and stretches in back seat. Girl slowly reaches up and wipes a small circle "
            "in the fogged window with one finger, peers through it at the dark beach outside. "
            "Subtle breath mist visible in the cold morning air."
        ),
    },
    {
        "filename": "02_coffee_hood",
        "still_prompt": (
            "Girl with back to camera, standing at the hood of a yellow Ford Bronco parked at Black's Beach La Jolla San Diego. "
            "Both hands wrapped around a dented metal thermos, steam visible rising. "
            "Oversized faded hoodie, bare legs below the hem, wet hair stuck flat down her back. "
            "Pacific Ocean and grey morning coastal haze behind her. Hood of Bronco in foreground. "
            "Flat overcast pre-dawn ambient light — no direct sun. Cool grey-blue sky, muted cold coastal palette. "
            "Slightly underexposed. Her wet hair catches the only light. No face visible. "
            "iPhone candid, shot close from behind, slight handheld tilt. "
            + UNIVERSAL
        ),
        "motion_prompt": (
            "Steam rises slowly from the thermos. Her hair lifts slightly in a coastal morning breeze. "
            "She adjusts her grip on the thermos with both hands, shoulders drop slightly as she exhales."
        ),
    },
    {
        "filename": "03_cliff_trail",
        "still_prompt": (
            "Girl walking away from camera up a sandy cliff trail at Black's Beach, Torrey Pines, La Jolla San Diego. "
            "Back to camera, surfboard tucked under one arm, other arm loose at her side. "
            "Oversized faded hoodie, bare legs below the hem, wet hair down her back. "
            "Low morning sun at a side angle — long diagonal shadow cast ahead of her on the sandy trail. "
            "Torrey Pines sandstone cliffs in the background, coastal scrub at trail edges. "
            "One bare foot lifted mid-stride. Warm sandy tones, slight morning haze. "
            "iPhone candid, handheld, slight tilt, documentary feel. No professional framing. "
            + UNIVERSAL
        ),
        "motion_prompt": (
            "She walks slowly up the trail, sand shifting under her bare feet, "
            "surfboard shifts slightly under her arm. Handheld camera sway follows her movement."
        ),
    },
    {
        "filename": "04_waters_edge",
        "still_prompt": (
            "Girl with back to camera standing at the very edge of the water at Black's Beach San Diego. "
            "Just came out of the ocean — oversized hoodie wet and dark at the hem, waterlogged fabric. "
            "Bare legs, wet sand under and between her feet. Wet hair stuck flat down her back. "
            "She stands still facing the Pacific Ocean. "
            "Flat grey-blue overcast morning coastal light — no direct sun, soft diffused ambient only. "
            "Small waves at her feet, seafoam on the sand. Wide framing shows full figure from behind, ocean horizon ahead. "
            "Cool muted blue-grey coastal tones. iPhone candid, slightly underexposed. "
            + UNIVERSAL
        ),
        "motion_prompt": (
            "A small wave slowly washes in over her feet and retreats, pulling wet sand back with it. "
            "Her hair shifts gently in the ocean breeze. She stays still."
        ),
    },
    {
        "filename": "05_outdoor_rinse",
        "still_prompt": (
            "Girl standing at an outdoor beach rinse shower pole at Black's Beach parking area. Back to camera. "
            "Eyes closed, head tilted slightly, water streaming over her wet hair and down her back. "
            "Oversized hoodie darkening and clinging as it soaks through. Bare legs below the hem. "
            "Yellow Ford Bronco visible parked in the soft background. "
            "Natural overcast daylight — water catches the light and creates slight overexposure on the stream, "
            "natural shadows in the wet fabric folds and creases. No artificial light. "
            "iPhone candid from slightly behind and to the side. Real shower, real moment. "
            + UNIVERSAL
        ),
        "motion_prompt": (
            "Water streams steadily over her hair and down her back. "
            "She slowly runs one hand through her wet hair, head tilts back slightly, "
            "eyes stay closed. Water splashes off her shoulders."
        ),
    },
    {
        "filename": "06_bronco_interior_dog",
        "still_prompt": (
            "Inside yellow Ford Bronco, mid-morning. Girl in oversized hoodie, bare legs, hair damp and half-dried. "
            "Folding a fleece blanket in the back cargo area of the Bronco. "
            "Dog — medium sized, dark fur — circling and stepping on the blanket. "
            "Lived-in interior: surfboard strapped along the side window, water bottles, small sandy towel. "
            "Dim interior ambient — rear cargo door open on one side, soft exterior daylight coming in from that side only. "
            "The far side of the interior is in natural shadow. Underexposed, warm interior tones. "
            "iPhone candid from just outside the rear cargo door. "
            + UNIVERSAL
        ),
        "motion_prompt": (
            "Dog steps on the corner of the blanket. She nudges it away gently with her knee and continues folding. "
            "Dog circles and tries again. Interior stays dim."
        ),
    },
    {
        "filename": "07_driver_seat_eyes_closed",
        "still_prompt": (
            "Girl in the driver's seat of a yellow Ford Bronco, head leaned back against the headrest, "
            "eyes closed, one hand resting loosely on the top of the steering wheel. "
            "Oversized faded hoodie, bare legs stretched forward. "
            "Morning sun coming through the lower windshield at a low angle — "
            "diagonal rays of warm gold light cross her chest and neck. "
            "Her jawline and one cheek catch the light. The other side of her face falls into natural shadow. "
            "Deep shadow under her chin, shadows from the visor above. Peaceful, tired expression. "
            "iPhone candid from the passenger seat. Warm muted interior tones, slight grain. "
            + UNIVERSAL
        ),
        "motion_prompt": (
            "Her chest rises and falls slowly with calm breathing. "
            "Morning light shifts slightly as a cloud passes, briefly softening the rays across her face before returning."
        ),
    },
    {
        "filename": "08_trigger_looks_at_camera",
        "still_prompt": (
            "Girl in the driver's seat of a yellow Ford Bronco looking directly into the camera. "
            "Tired, natural, intimate expression — not posing, caught in a real moment, unstyled. "
            "Oversized faded hoodie, bare legs, wet hair half-dried with pieces stuck to her neck and cheek. "
            "Morning light through the windshield lights one side of her face and catches her eye. "
            "The other side of her face and her hair are in natural shadow. No makeup visible. "
            "Natural blue-green eyes looking straight into the lens, slightly heavy-lidded. "
            "iPhone held from the passenger seat at chest level. Close personal framing, direct eye contact. "
            "Muted warm tones. Visible grain. She is just existing — no performance. "
            + UNIVERSAL
        ),
        "motion_prompt": (
            "She holds direct eye contact. Blinks slowly once. A barely visible breath. "
            "Her gaze drifts briefly to the window, then returns to the camera. "
            "Nothing else moves."
        ),
    },
    {
        "filename": "09_reaction_ring_light",
        "still_prompt": (
            "Girl inside yellow Ford Bronco, caught mid-motion adjusting her hair while looking into the rearview mirror. "
            "A small clip-on ring light mounted on the dashboard, warm LED glow — "
            "the only artificial light in the frame, creating a warm halo on her face and in the mirror. "
            "Rest of the interior is dim with cool ambient, creating natural contrast between the warm ring-lit zone "
            "and the darker vehicle interior. Hand raised mid-motion toward her hair. "
            "Expression unreadable — mid-thought, not aware of the camera yet. "
            "iPhone candid from the back seat between the front seats. "
            "Warm ring light color cast on her face, cool dim shadows behind her. "
            + UNIVERSAL
        ),
        "motion_prompt": (
            "She pauses mid-motion with hand in her hair, sensing the camera is still on. "
            "Slowly lowers her hand from her hair and turns from the mirror to look directly at the camera. "
            "Holds the look — not startled, just caught. Unreadable. A beat of stillness."
        ),
    },
]


def poll(task_id, timeout=600, label=""):
    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            r = requests.get(f"{BASE_URL}/predictions/{task_id}/result", headers=headers, timeout=30)
            data = r.json().get("data", {})
            status = data.get("status")
            if status == "completed":
                return data["outputs"][0]
            if status == "failed":
                raise RuntimeError(f"{label} failed: {data.get('error')}")
        except requests.RequestException as e:
            print(f"  [{label}] poll error: {e}, retrying...")
        time.sleep(10 + random.uniform(0, 3))
    raise RuntimeError(f"{label} timeout after {timeout}s")


def run_scene(scene):
    name = scene["filename"]
    clip_path  = os.path.join(CLIPS_DIR, f"{name}.mp4")
    still_path = os.path.join(STILLS_DIR, f"{name}.jpg")
    url_cache  = os.path.join(STILLS_DIR, f"{name}.cdn_url")

    if os.path.exists(clip_path):
        print(f"  SKIP {name} (clip exists)")
        return name, True

    # Stage 1 — Seedream 2K still
    if os.path.exists(url_cache):
        with open(url_cache) as f:
            still_url = f.read().strip()
        print(f"  [STILL CACHED] {name}")
    else:
        print(f"  [STILL] {name} -> Seedream...")
        for attempt in range(3):
            resp = requests.post(
                f"{BASE_URL}/{IMG_MODEL}",
                headers=headers,
                json={
                    "images": REFS,
                    "prompt": scene["still_prompt"],
                    "size": "2048*3640",
                },
                timeout=30,
            )
            if resp.status_code == 200:
                break
            print(f"  [{name}] Seedream {resp.status_code}: {resp.text[:200]} — retry {attempt+1}/3")
            time.sleep(15 + attempt * 10)
        resp.raise_for_status()
        task_id = resp.json()["data"]["id"]
        still_url = poll(task_id, label=f"{name}[still]")

        # cache CDN URL for resume
        with open(url_cache, "w") as f:
            f.write(still_url)

        # download still locally
        img_r = requests.get(still_url, timeout=120, stream=True)
        img_r.raise_for_status()
        with open(still_path, "wb") as f:
            for chunk in img_r.iter_content(65536):
                f.write(chunk)
        print(f"  [STILL DONE] {name}")

    # Stage 2 — Seedance 2.0 animation
    print(f"  [VIDEO] {name} -> Seedance 2.0...")
    for attempt in range(3):
        resp = requests.post(
            f"{BASE_URL}/{VID_MODEL}",
            headers=headers,
            json={
                "image": still_url,
                "prompt": scene["motion_prompt"],
                "resolution": "720p",
                "duration": 4,
                "aspect_ratio": "9:16",
                "generate_audio": False,
            },
            timeout=30,
        )
        if resp.status_code == 200:
            break
        print(f"  [{name}] Seedance {resp.status_code}: {resp.text[:200]} — retry {attempt+1}/3")
        time.sleep(20 + attempt * 15)
    resp.raise_for_status()
    task_id = resp.json()["data"]["id"]
    print(f"  [{name}] Seedance task: {task_id}")

    video_url = poll(task_id, label=f"{name}[video]")

    vid_r = requests.get(video_url, timeout=300, stream=True)
    vid_r.raise_for_status()
    with open(clip_path, "wb") as f:
        for chunk in vid_r.iter_content(65536):
            f.write(chunk)

    print(f"  [DONE] {name}.mp4")
    return name, True


print("=" * 60)
print("SEEDANCE REEL PIPELINE — Day in the Bronco (9 scenes)")
print("Stage 1: Seedream 2K stills  — $0.04 × 9 = $0.36")
print("Stage 2: Seedance 2.0 clips  — $0.48 × 9 = $4.32")
print("Total: $4.68 | 720p | 9:16 | 4s per clip | no audio")
print("=" * 60 + "\n")

with ThreadPoolExecutor(max_workers=2) as pool:
    futures = {pool.submit(run_scene, s): s for s in SCENES}
    for fut in as_completed(futures):
        scene = futures[fut]
        try:
            fname, _ = fut.result()
            print(f"[COMPLETE] {fname}")
        except Exception as e:
            print(f"[ERROR] {scene['filename']}: {e}")

print(f"\nStills -> {STILLS_DIR}")
print(f"Clips  -> {CLIPS_DIR}")
print("Stitch order: 01 -> 02 -> 03 -> 04 -> 05 -> 06 -> 07 -> 08 -> 09")

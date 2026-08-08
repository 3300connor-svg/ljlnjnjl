import sys, os
sys.path.insert(0, r"C:\Users\pheno\Downloads\wavespeed-batch-api\wavespeed-batch-api")
from wavespeed_client import WaveSpeedClient

API_KEY    = "wsk_live_MWD0E5QYAIV4CP2S3ya2QPZvTApxlw8oBSqPaeLIZ-E"
AVATAR_URL = "https://i.ibb.co/L71FBJn/456d6aea768544dc80d45f20084e5d16.png"
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR = os.path.join(SCRIPT_DIR, "outputs", "nova_b3")
CHECKPOINT = os.path.join(SCRIPT_DIR, "checkpoint_nova_b3.json")

JOBS = [
    {
        "prompt": "Sharp crisp iPhone-style photo inside Wendy's, girl standing in line completely focused on her phone looking down at her screen, completely unaware of the camera, thick full round ass prominent in tight fitted jeans — no necklace — other customers and bright fast food interior sharply in focus around her, no blur, no motion blur, natural overhead fluorescent lighting. Authentic sharp candid. Use the reference image to accurately reproduce her facial features, body shape, proportions, and curves.",
        "filename": "009_wendys_sharp_phone_necklace.jpg",
        "metadata": {"type": "candid", "location": "Wendys"}
    },
    {
        "prompt": "Overhead bedroom selfie looking straight down into camera, girl lying back on a soft white pillow, phone held directly above her face, frame shows chest to face only — generous natural cleavage visible from above angle, soft pouty lips, sleepy natural expression, no makeup, messy hair spread on pillow, warm soft bedroom light, no arms visible in frame. Raw, intimate, cozy iPhone-style photo. Use the reference image to accurately reproduce her facial features, body shape, proportions, and curves.",
        "filename": "011_bed_overhead_chest_poutylips.jpg",
        "metadata": {"type": "selfie-overhead", "location": "bedroom"}
    },
    {
        "prompt": "Bedroom mirror selfie, girl facing forward in a thin champagne silk slip dress — absolutely no bra, nipples clearly and naturally poking through the delicate silk fabric — thick toned legs, full round prominent ass, generous chest, natural soft pouty expression looking directly at her reflection, warm lamp light on skin, unmade bed visible in background. Raw, unedited, authentic social media mirror selfie. Use the reference image to accurately reproduce her facial features, body shape, proportions, and curves.",
        "filename": "008_mirror_bedroom_slipDress_forward_nipple.jpg",
        "metadata": {"type": "mirror", "location": "bedroom"}
    },
    {
        "prompt": "Candid amateur iPhone photo taken by a friend, girl walking along the shallow edge of the tide with water at her ankles, thin string bikini top and matching bottoms — nipples naturally poking through the thin wet bikini fabric — thick toned legs, full round ass and generous chest, authentic tongue-out expression looking playfully toward the camera mid-walk, soft even beach light, ocean behind her, spontaneous and real. Raw, unedited authentic beach candid. Use the reference image to accurately reproduce her facial features, body shape, proportions, and curves.",
        "filename": "007_beach_tide_tongueout_nipple.jpg",
        "metadata": {"type": "third-party", "location": "beach tide"}
    },
    {
        "prompt": "iPhone-style selfie, girl taking her own photo, wearing a full real oversized hoodie — nipples subtly but clearly poking through the soft thick fabric, no cleavage — grey boxer-style underwear visible below the hoodie hem, natural subtle smile, warm ambient bedroom light, messy casual hair, relaxed and genuine. Authentic amateur iPhone aesthetic without literally showing the phone model. Use the reference image to accurately reproduce her facial features, body shape, proportions, and curves.",
        "filename": "001_selfie_hoodie_grey_boxers_nipple.jpg",
        "metadata": {"type": "selfie", "location": "bedroom"}
    },
]

def progress(done, total, last):
    print(f"[{done}/{total}] {last}", flush=True)

client = WaveSpeedClient(api_key=API_KEY)
result = client.batch_generate(
    jobs=JOBS,
    avatar_url=AVATAR_URL,
    output_dir=OUTPUT_DIR,
    size=(1024, 1792),
    max_concurrent=5,
    progress_callback=progress,
    checkpoint_path=CHECKPOINT,
)
print(f"Done: {result['n_success']}/{result['n_total']} | Failed: {result['n_failed']} | {result['duration_s']:.0f}s")

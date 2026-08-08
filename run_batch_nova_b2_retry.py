import sys, os
sys.path.insert(0, r"C:\Users\pheno\Downloads\wavespeed-batch-api\wavespeed-batch-api")
from wavespeed_client import WaveSpeedClient

API_KEY    = "wsk_live_MWD0E5QYAIV4CP2S3ya2QPZvTApxlw8oBSqPaeLIZ-E"
AVATAR_URL = "https://i.ibb.co/L71FBJn/456d6aea768544dc80d45f20084e5d16.png"
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR = os.path.join(SCRIPT_DIR, "outputs", "nova_b2")
CHECKPOINT = os.path.join(SCRIPT_DIR, "checkpoint_nova_b2_retry.json")

JOBS = [
    {
        "prompt": "Candid bedroom selfie, girl in a cropped oversized hoodie with no bra — subtle nipple outline through thin fabric — and tiny black biker shorts showing thick toned legs, sitting on the edge of her bed leaning forward slightly, warm bedside lamp glow, natural relaxed slightly sleepy expression, messy hair. Slightly imperfect framing. Raw, unedited, authentic phone photo. Use the reference image to accurately reproduce her facial features, body shape, proportions, and curves.",
        "filename": "001_selfie_bedroom_hoodie_sexy.jpg",
        "metadata": {"type": "selfie", "location": "bedroom", "outfit": "cropped hoodie+biker shorts"}
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
    max_concurrent=1,
    progress_callback=progress,
    checkpoint_path=CHECKPOINT,
)
print(f"Done: {result['n_success']}/{result['n_total']} | Failed: {result['n_failed']} | {result['duration_s']:.0f}s")

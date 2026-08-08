import sys, os
sys.path.insert(0, r"C:\Users\pheno\Downloads\wavespeed-batch-api\wavespeed-batch-api")
from wavespeed_client import WaveSpeedClient

API_KEY    = "wsk_live_MWD0E5QYAIV4CP2S3ya2QPZvTApxlw8oBSqPaeLIZ-E"
AVATAR_URL = "https://i.ibb.co/L71FBJn/456d6aea768544dc80d45f20084e5d16.png"
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR = os.path.join(SCRIPT_DIR, "outputs", "nova_b4")
CHECKPOINT = os.path.join(SCRIPT_DIR, "checkpoint_nova_b4_retry.json")

JOBS = [
    {
        "prompt": "Bedroom mirror selfie facing forward, girl in a delicate thin satin slip dress — fabric so thin the natural outline of her nipples shows through, no bra — thick toned legs, full round figure with generous chest and curves, phone held naturally at chest with proportionate size in the reflection, soft genuine pouty expression looking directly at her reflection, warm amber bedside lamp, rumpled bedding behind her. Raw unedited mirror selfie. Use the reference image to accurately reproduce her facial features, body shape, proportions, and curves.",
        "filename": "008_mirror_bedroom_slip_forward.jpg",
        "metadata": {"type": "mirror", "location": "bedroom"}
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

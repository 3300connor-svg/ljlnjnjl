import sys, os
sys.path.insert(0, r"C:\Users\pheno\Downloads\wavespeed-batch-api\wavespeed-batch-api")
from wavespeed_client import WaveSpeedClient

API_KEY    = "wsk_live_MWD0E5QYAIV4CP2S3ya2QPZvTApxlw8oBSqPaeLIZ-E"
SOURCE_IMG = "https://i.ibb.co/0jKPmhcG/009-restaurant-night-coastal-edited.jpg"
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR = os.path.join(SCRIPT_DIR, "outputs", "restaurant_edit")
CHECKPOINT = os.path.join(SCRIPT_DIR, "checkpoint_restaurant_edit.json")

JOBS = [
    {
        "prompt": (
            "Keep the girl in the foreground exactly as she is — same pose, same outfit, same lighting on her face and body. "
            "Transform the setting into a warm coastal restaurant at night. "
            "Add a waiter in dark clothing facing completely away from camera, carrying plates toward a nearby table. "
            "Soft background of couples and small groups dining, all with their backs or sides to camera — no faces visible toward camera. "
            "Warm ambient candlelight and dim overhead restaurant glow in background. "
            "Make the overall image quality look like a candid iPhone shot taken in the moment — "
            "slightly imperfect handheld exposure, natural lens characteristics, mild highlight overexposure, "
            "subtle vignette at frame edges, no professional lighting, no studio fill light, "
            "warm ambient tones from restaurant lighting. Approachable, candid, girl-next-door feel."
        ),
        "filename": "009_restaurant_iphone_v2.jpg",
        "metadata": {"type": "restaurant-edit"}
    },
]

def progress(done, total, last):
    print(f"[{done}/{total}] {last}", flush=True)

client = WaveSpeedClient(api_key=API_KEY)
result = client.batch_generate(
    jobs=JOBS,
    avatar_url=SOURCE_IMG,
    output_dir=OUTPUT_DIR,
    size=(1024, 1792),
    max_concurrent=1,
    progress_callback=progress,
    checkpoint_path=CHECKPOINT,
)
print(f"Done: {result['n_success']}/{result['n_total']} | Failed: {result['n_failed']} | {result['duration_s']:.0f}s")

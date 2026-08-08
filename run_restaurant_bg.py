import sys, os
sys.path.insert(0, r"C:\Users\pheno\Downloads\wavespeed-batch-api\wavespeed-batch-api")
from wavespeed_client import WaveSpeedClient

API_KEY    = "wsk_live_MWD0E5QYAIV4CP2S3ya2QPZvTApxlw8oBSqPaeLIZ-E"
SOURCE_IMG = "https://i.ibb.co/0jKPmhcG/009-restaurant-night-coastal-edited.jpg"
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR = os.path.join(SCRIPT_DIR, "outputs", "restaurant_edit")
CHECKPOINT = os.path.join(SCRIPT_DIR, "checkpoint_restaurant_bg.json")

JOBS = [
    {
        "prompt": (
            "Do not change the girl in the foreground at all — same pose, same face, same outfit, same lighting on her. "
            "Do not change the location or setting. "
            "Only change the background: populate it with a few people seated at tables dining, "
            "backs and sides to camera, no faces visible toward the lens. "
            "Replace the background lighting with uneven, imperfect ambient restaurant light — "
            "warm but inconsistent, dim patches, natural candlelight flicker feel, "
            "no clean professional lighting rigs, slightly underexposed background. "
            "Everything in the foreground stays identical."
        ),
        "filename": "009_restaurant_bg_filled.jpg",
        "metadata": {"type": "restaurant-bg-fill"}
    },
]

def progress(done, total, last):
    print(f"[{done}/{total}] {last}", flush=True)

client = WaveSpeedClient(api_key=API_KEY)
result = client.batch_generate(
    jobs=JOBS,
    avatar_url=SOURCE_IMG,
    output_dir=OUTPUT_DIR,
    size=(2048, 3640),
    max_concurrent=1,
    progress_callback=progress,
    checkpoint_path=CHECKPOINT,
)
print(f"Done: {result['n_success']}/{result['n_total']} | Failed: {result['n_failed']} | {result['duration_s']:.0f}s")

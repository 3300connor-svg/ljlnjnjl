import sys, os
sys.path.insert(0, r"C:\Users\pheno\Downloads\wavespeed-batch-api\wavespeed-batch-api")
from wavespeed_client import WaveSpeedClient

API_KEY    = "wsk_live_MWD0E5QYAIV4CP2S3ya2QPZvTApxlw8oBSqPaeLIZ-E"
AVATAR_URL = "https://i.ibb.co/8gd2SqKH/download.jpg"
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR = os.path.join(SCRIPT_DIR, "outputs", "nova_b6")
CHECKPOINT = os.path.join(SCRIPT_DIR, "checkpoint_nova_b6_nude_v3.json")

JOBS = [
    {
        "prompt": "Candid photo at Black's Beach La Jolla San Diego, late afternoon, girl standing near the water completely nude, wet hair stuck to her face and neck, small water droplets on her skin. Close personal framing showing her full figure. Tall sandstone Torrey Pines cliffs in the background. Flat natural ambient coastal daylight, no dramatic highlights, no glowing skin, no cinematic lighting — just the real unfiltered look of being outside in late afternoon shade and haze. Slightly noisy exposure, muted color tones, natural skin texture visible, imperfect focus edges. Unposed, caught off guard, genuinely in the moment. Golden sun-kissed Brazilian complexion, lighter warm skin. Natural blue eyes with green center. Sun-kissed brunette hair with natural blonde highlights. Soft light freckles. Youthful 19-21, surfer girl. Consistent full figure — thick toned legs, round ass, generous chest. No studio lighting, no artificial glow, no highlighting. Natural flat ambient light. Use the reference image to accurately reproduce her facial features, body shape, proportions, and curves.",
        "filename": "004_blacks_beach_nude_v3.jpg",
        "metadata": {"type": "candid", "location": "Blacks Beach ambient"}
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

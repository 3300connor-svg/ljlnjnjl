import sys, os
sys.path.insert(0, r"C:\Users\pheno\Downloads\wavespeed-batch-api\wavespeed-batch-api")
from wavespeed_client import WaveSpeedClient

API_KEY    = "wsk_live_MWD0E5QYAIV4CP2S3ya2QPZvTApxlw8oBSqPaeLIZ-E"
AVATAR_URL = "https://i.ibb.co/8gd2SqKH/download.jpg"
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR = os.path.join(SCRIPT_DIR, "outputs", "nova_b6_side")
CHECKPOINT = os.path.join(SCRIPT_DIR, "checkpoint_nova_b6_side.json")

JOBS = [
    {
        "prompt": "Candid photo at Black's Beach San Diego, girl lying on her side on the sand, completely nude, chest naturally falling toward the sand with gravity, generous full breasts hanging down naturally. She is looking downward and slightly away from the camera, expression quiet and a little shy, gaze cast down toward the sand. Camera at ground level, close personal framing, slightly above her eye line. Wet salty hair splayed out on the sand. Warm muted late afternoon coastal light, no cinematic glow, flat natural ambient with slight directional warmth from low sun. Slightly imperfect exposure, muted warm tones, noisy image, natural skin texture. Unposed, genuinely in the moment. Golden sun-kissed Brazilian complexion, lighter warm skin. Natural blue eyes with green center. Sun-kissed brunette hair with natural blonde highlights. Soft light freckles across nose and cheeks. Youthful 19-21, surfer girl, coastal San Diego. Consistent full figure — thick toned legs, round prominent ass, generous chest. No studio lighting, no artificial glow. Use the reference image to accurately reproduce her facial features, body shape, proportions, and curves.",
        "filename": "005_blacks_beach_side_lay.jpg",
        "metadata": {"type": "candid-side", "location": "Blacks Beach lying on side"}
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

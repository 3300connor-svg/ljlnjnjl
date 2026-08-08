import sys, os
sys.path.insert(0, r"C:\Users\pheno\Downloads\wavespeed-batch-api\wavespeed-batch-api")
from wavespeed_client import WaveSpeedClient

API_KEY    = "wsk_live_MWD0E5QYAIV4CP2S3ya2QPZvTApxlw8oBSqPaeLIZ-E"
AVATAR_URL = "https://i.ibb.co/8gd2SqKH/download.jpg"
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR = os.path.join(SCRIPT_DIR, "outputs", "nova_b6_behind")
CHECKPOINT = os.path.join(SCRIPT_DIR, "checkpoint_nova_b6_behind.json")

JOBS = [
    {
        "prompt": "Candid photo from directly behind at Black's Beach La Jolla San Diego, girl bending forward to pick up her surfboard from the sand, shot from behind showing her full back and thick round ass prominently, completely nude, wet salty hair hanging forward, water droplets on her back and skin. Late afternoon light — warm but understated, natural coastal haze, no cinematic glow, real outdoor ambient with slight directional warmth. Slightly imperfect exposure, muted warm tones, natural skin texture. Tall sandstone Torrey Pines cliffs visible in background. Unposed, caught mid-action. Golden sun-kissed Brazilian complexion, lighter warm skin. Sun-kissed brunette hair with natural blonde highlights. Soft light freckles. Youthful 19-21, surfer girl, coastal San Diego. Consistent full figure — thick toned legs, round prominent ass, generous chest. No studio lighting, no artificial glow. Use the reference image to accurately reproduce her facial features, body shape, proportions, and curves.",
        "filename": "004_blacks_beach_behind_bend.jpg",
        "metadata": {"type": "candid-behind", "location": "Blacks Beach from behind"}
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

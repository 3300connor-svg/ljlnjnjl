import sys, os
sys.path.insert(0, r"C:\Users\pheno\Downloads\wavespeed-batch-api\wavespeed-batch-api")
from wavespeed_client import WaveSpeedClient

API_KEY    = "wsk_live_MWD0E5QYAIV4CP2S3ya2QPZvTApxlw8oBSqPaeLIZ-E"
AVATAR_URL = "https://i.ibb.co/8gd2SqKH/download.jpg"
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR = os.path.join(SCRIPT_DIR, "outputs", "nova_b6_behind")
CHECKPOINT = os.path.join(SCRIPT_DIR, "checkpoint_nova_b6_behind_v2.json")

JOBS = [
    {
        "prompt": "Candid photo shot from directly behind, close up, camera low and tight on her form, girl bending forward at the waist at Black's Beach San Diego, completely nude, thick round ass filling the frame prominently, wet skin with water droplets, wet salty hair hanging forward. Torrey Pines sandstone cliffs visible in background. Natural flat ambient coastal light, no studio glow, slightly imperfect exposure, muted warm tones. Unposed, in the moment. Golden sun-kissed Brazilian complexion, lighter warm skin. Youthful 19-21, surfer girl. Consistent full figure — thick toned legs, round prominent ass. No artificial lighting. Use the reference image to accurately reproduce her facial features, body shape, proportions, and curves.",
        "filename": "004_blacks_beach_behind_v2.jpg",
        "metadata": {"type": "candid-behind-closeup", "location": "Blacks Beach behind"}
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

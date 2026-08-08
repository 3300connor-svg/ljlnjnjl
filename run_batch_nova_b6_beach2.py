import sys, os
sys.path.insert(0, r"C:\Users\pheno\Downloads\wavespeed-batch-api\wavespeed-batch-api")
from wavespeed_client import WaveSpeedClient

API_KEY    = "wsk_live_MWD0E5QYAIV4CP2S3ya2QPZvTApxlw8oBSqPaeLIZ-E"
AVATAR_URL = "https://i.ibb.co/8gd2SqKH/download.jpg"
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR = os.path.join(SCRIPT_DIR, "outputs", "nova_b6")
CHECKPOINT = os.path.join(SCRIPT_DIR, "checkpoint_nova_b6_beach2.json")

UNIVERSAL = "Golden sun-kissed Brazilian complexion, lighter warm skin. Natural blue eyes with green center. Sun-kissed brunette hair with natural blonde highlights. Soft light freckles across nose and cheeks. Youthful 19-21, surfer girl, coastal San Diego lifestyle. Consistent full figure — thick toned legs, round ass, generous chest. No studio lighting, no artificial glow. Natural ambient light. Use the reference image to accurately reproduce her facial features, body shape, proportions, and curves."

JOBS = [
    {
        "prompt": f"Candid photo at Black's Beach La Jolla San Diego, girl bending forward naturally to pick up her surfboard from the sand, completely nude, wet salty hair hanging forward and clinging to her face and shoulders, water droplets on her skin. Full figure prominent from this angle. Late afternoon light — warm but understated, natural coastal haze with soft golden warmth, no cinematic highlights or glowing skin, just real outdoor ambient with slight directional warmth from low sun. Slightly imperfect exposure, muted warm tones, natural skin texture visible. Tall sandstone Torrey Pines cliffs in background. Unposed, caught mid-action, genuinely in the moment. {UNIVERSAL}",
        "filename": "004_blacks_beach_bend_surfboard.jpg",
        "metadata": {"type": "candid", "location": "Blacks Beach bending surfboard"}
    },
    {
        "prompt": f"Candid photo at Black's Beach La Jolla San Diego, late afternoon, girl standing near the water wearing a black string bikini, wet hair stuck to her face and neck, small water droplets on her skin. Close personal framing showing her full figure. Tall sandstone Torrey Pines cliffs in the background. Flat natural ambient coastal daylight, no dramatic highlights, no glowing skin, no cinematic lighting — real unfiltered outdoor light with slight afternoon warmth. Slightly noisy exposure, muted color tones, natural skin texture visible. Unposed, caught off guard, genuinely in the moment. {UNIVERSAL}",
        "filename": "004_blacks_beach_bikini_v3.jpg",
        "metadata": {"type": "candid", "location": "Blacks Beach black bikini"}
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
    max_concurrent=2,
    progress_callback=progress,
    checkpoint_path=CHECKPOINT,
)
print(f"Done: {result['n_success']}/{result['n_total']} | Failed: {result['n_failed']} | {result['duration_s']:.0f}s")

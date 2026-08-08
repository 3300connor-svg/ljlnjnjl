import sys, os
sys.path.insert(0, r"C:\Users\pheno\Downloads\wavespeed-batch-api\wavespeed-batch-api")
from wavespeed_client import WaveSpeedClient

API_KEY    = "wsk_live_MWD0E5QYAIV4CP2S3ya2QPZvTApxlw8oBSqPaeLIZ-E"
AVATAR_URL = "https://i.ibb.co/8gd2SqKH/download.jpg"
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR = os.path.join(SCRIPT_DIR, "outputs", "nova_b6")
CHECKPOINT = os.path.join(SCRIPT_DIR, "checkpoint_nova_b6_retry.json")

UNIVERSAL = "Golden sun-kissed Brazilian complexion, lighter warm skin. Natural blue eyes with green center. Sun-kissed brunette hair with natural blonde highlights, slightly wavy beachy texture. Soft light freckles across nose and cheeks. Youthful 19-21, soft natural features. Surfer girl, coastal San Diego lifestyle. Consistent full figure — thick toned legs, round ass, generous chest. Amateur iPhone quality, natural lens characteristics, slightly imperfect exposure, ambient light inconsistencies. No studio lighting. No iPhone UI frame."

JOBS = [
    {
        "prompt": f"Selfie-angle beach photo from arm's length, camera close to her face looking slightly downward, no phone visible in frame. Girl in a black triangle bikini top and cutoff denim shorts, bright natural California beach light, white sand and ocean behind her. Playful tongue-out expression looking straight into the camera, hair blowing from the ocean breeze. Close framing showing face, chest, and upper body naturally. Slight natural lens flare from sun, authentic selfie POV. {UNIVERSAL} Use the reference image to accurately reproduce her facial features, body shape, proportions, and curves.",
        "filename": "002_beach_selfie_tongueout_v2.jpg",
        "metadata": {"type": "selfie-pov", "location": "beach"}
    },
    {
        "prompt": f"Candid amateur photo at Black's Beach La Jolla San Diego, late golden hour afternoon, girl standing near the water's edge completely nude, wet hair clinging to her face and shoulders, small water droplets glistening on her skin from the ocean. Up close and personal framing showing her full body in revealing detail. Tall golden sandstone Torrey Pines cliffs glowing in warm late afternoon light behind her, long raking shadows across the sand, warm orange-gold sunlight hitting her body from low on the horizon. Random ambient light inconsistencies, slight coastal haze, natural lens flare, slightly imperfect exposure. Unposed, genuinely in the moment, authentic and candid like someone just snapped it. {UNIVERSAL} Use the reference image to accurately reproduce her facial features, body shape, proportions, and curves.",
        "filename": "004_blacks_beach_nude_v2.jpg",
        "metadata": {"type": "candid", "location": "Blacks Beach golden hour"}
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

import sys, os
sys.path.insert(0, r"C:\Users\pheno\Downloads\wavespeed-batch-api\wavespeed-batch-api")
from wavespeed_client import WaveSpeedClient

API_KEY    = "wsk_live_MWD0E5QYAIV4CP2S3ya2QPZvTApxlw8oBSqPaeLIZ-E"
AVATAR_URL = "https://i.ibb.co/L71FBJn/456d6aea768544dc80d45f20084e5d16.png"
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR = os.path.join(SCRIPT_DIR, "outputs", "nova_b4")
CHECKPOINT = os.path.join(SCRIPT_DIR, "checkpoint_nova_b4.json")

JOBS = [
    {
        "prompt": "Amateur iPhone selfie, girl taking a photo of herself in her bedroom, wearing a soft worn oversized hoodie — thin enough that the natural outline of her nipples is faintly visible through the fabric — with grey cotton boxer-cut underwear showing below the hem. Subtle genuine smile like she's mid-thought, warm dim bedroom light, slightly messy hair. Phone held at face level, natural casual framing. Raw iPhone aesthetic. Use the reference image to accurately reproduce her facial features, body shape, proportions, and curves.",
        "filename": "001_selfie_hoodie_grey_boxers.jpg",
        "metadata": {"type": "selfie", "location": "bedroom"}
    },
    {
        "prompt": "Candid beach photo taken by a friend on an iPhone, girl standing still at the shoreline with soft waves near her feet, wearing a small fitted string bikini — thin fabric with the natural outline of her nipples visible — thick curves, round ass, generous chest. Cute expression with bright eyes and a genuine playful smile like she's about to laugh, hair slightly wind-tousled, soft warm overcast beach light with no harsh glare, ocean behind her. Spontaneous and joyful. Raw unedited amateur iPhone. Use the reference image to accurately reproduce her facial features, body shape, proportions, and curves.",
        "filename": "007_beach_standing_cute_smile.jpg",
        "metadata": {"type": "third-party", "location": "beach"}
    },
    {
        "prompt": "Bedroom mirror selfie facing forward, girl in a delicate thin satin slip dress — fabric so thin the natural outline of her nipples shows through, no bra — thick toned legs, full round figure with generous chest and curves, phone held naturally at chest with proportionate size in the reflection, soft genuine pouty expression looking directly at her reflection, warm amber bedside lamp, rumpled bedding behind her. Raw unedited mirror selfie. Use the reference image to accurately reproduce her facial features, body shape, proportions, and curves.",
        "filename": "008_mirror_bedroom_slip_forward.jpg",
        "metadata": {"type": "mirror", "location": "bedroom"}
    },
    {
        "prompt": "Sharp clear iPhone photo inside Wendy's, girl standing in line completely absorbed scrolling her phone — no idea the photo is being taken — thick full round ass prominent in tight fitted jeans, no necklace, simple casual top, other customers and bright fast food interior sharp and in focus around her, natural overhead fluorescent lighting. Completely candid, no blur. Use the reference image to accurately reproduce her facial features, body shape, proportions, and curves.",
        "filename": "009_wendys_candid_sharp.jpg",
        "metadata": {"type": "candid", "location": "Wendys"}
    },
    {
        "prompt": "Overhead bedroom selfie, girl lying back on soft white bedding looking up into the camera held directly above her, frame shows face and décolletage — natural cleavage visible from the above angle, low-cut top — soft pouty lips slightly parted, sleepy natural eyes, no makeup, hair fanned out casually on the pillow, warm soft ambient bedroom light. Intimate and natural. Raw iPhone aesthetic. Use the reference image to accurately reproduce her facial features, body shape, proportions, and curves.",
        "filename": "011_bed_overhead_cleavage.jpg",
        "metadata": {"type": "selfie-overhead", "location": "bedroom"}
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
    max_concurrent=5,
    progress_callback=progress,
    checkpoint_path=CHECKPOINT,
)
print(f"Done: {result['n_success']}/{result['n_total']} | Failed: {result['n_failed']} | {result['duration_s']:.0f}s")

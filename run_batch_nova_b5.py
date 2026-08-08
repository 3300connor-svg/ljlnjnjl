import sys, os
sys.path.insert(0, r"C:\Users\pheno\Downloads\wavespeed-batch-api\wavespeed-batch-api")
from wavespeed_client import WaveSpeedClient

API_KEY    = "wsk_live_MWD0E5QYAIV4CP2S3ya2QPZvTApxlw8oBSqPaeLIZ-E"
AVATAR_URL = "https://i.ibb.co/8gd2SqKH/download.jpg"
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR = os.path.join(SCRIPT_DIR, "outputs", "nova_b5")
CHECKPOINT = os.path.join(SCRIPT_DIR, "checkpoint_nova_b5.json")

JOBS = [
    {
        "prompt": "Candid iPhone selfie, girl sitting on the edge of her bed taking a photo of herself, wearing a full oversized worn hoodie — thin enough that the natural outline of her nipples is faintly visible — grey cotton boxer-cut underwear visible below the hem. Subtle genuine smile, warm dim bedroom light, messy wavy hair with natural blonde highlights. Raw, authentic, not staged. Golden sun-kissed Brazilian complexion, lighter warm skin. Natural blue eyes with green center. Soft light freckles. Youthful 19-21, surfer girl aesthetic. No iPhone UI frame or screen border. Use the reference image to accurately reproduce her facial features, body shape, proportions, and curves.",
        "filename": "001_selfie_bedroom_hoodie.jpg",
        "metadata": {"type": "selfie", "location": "bedroom"}
    },
    {
        "prompt": "Candid photo taken by a friend at a dimly lit cozy cafe, girl at a dark wooden table with an open MacBook and coffee, wearing a thin ribbed white tank top — no bra, subtle natural nipple outline through fabric — natural cleavage, thick legs crossed, looking down at her screen naturally. Low warm amber lighting, moody. Golden sun-kissed Brazilian complexion, lighter warm skin. Natural blue eyes with green center. Brunette hair with natural blonde highlights, wavy. Soft light freckles. Youthful 19-21, surfer girl aesthetic. Amateur iPhone, not studio. Use the reference image to accurately reproduce her facial features, body shape, proportions, and curves.",
        "filename": "003_cafe_homework_dark.jpg",
        "metadata": {"type": "third-party", "location": "cafe"}
    },
    {
        "prompt": "Mirror selfie in a boutique dressing room, girl holding phone naturally at chest height facing a large full-length mirror, wearing a fitted dark emerald satin midi dress. Mirror accurately reflects her complete figure and phone. Relaxed natural expression, effortless, not posed. Warm soft boutique lighting. Golden sun-kissed Brazilian complexion, lighter warm skin. Natural blue eyes with green center. Brunette hair with natural blonde highlights, loose waves. Soft light freckles. Youthful 19-21. Amateur iPhone, not studio. Use the reference image to accurately reproduce her facial features, body shape, proportions, and curves.",
        "filename": "004a_mirror_boutique_bodycon.jpg",
        "metadata": {"type": "mirror", "location": "boutique"}
    },
    {
        "prompt": "Mirror selfie in a mall changing room, girl holding phone at waist height facing a full-length mirror, wearing a form-fitting bodycon mini dress in dark green. Mirror accurately reflects her full figure. Relaxed natural young expression, genuine and effortless, not posed. Warm overhead lighting. Golden sun-kissed Brazilian complexion, lighter warm skin. Natural blue eyes with green center. Brunette hair with natural blonde highlights. Soft light freckles. Youthful 19-21. Amateur iPhone, not studio. Use the reference image to accurately reproduce her facial features, body shape, proportions, and curves.",
        "filename": "004b_mirror_mall_bodycon.jpg",
        "metadata": {"type": "mirror", "location": "mall"}
    },
    {
        "prompt": "Candid photo taken by the driver, girl in the passenger seat of a Ford Bronco, wearing a fitted white v-neck tee — no bra, natural cleavage visible — golden hour light flooding through the window, natural relaxed soft smile looking toward the camera, thick toned legs. Golden sun-kissed Brazilian complexion, lighter warm skin. Natural blue eyes with green center. Brunette hair with natural blonde highlights, slightly wavy. Soft light freckles. Youthful 19-21, surfer girl aesthetic. Authentic candid, amateur iPhone. Use the reference image to accurately reproduce her facial features, body shape, proportions, and curves.",
        "filename": "005_car_bronco_passenger.jpg",
        "metadata": {"type": "third-party", "location": "Ford Bronco"}
    },
    {
        "prompt": "Mirror selfie at a premium gym, girl in dusty rose seamless sports bra and matching high-waist leggings — no bra, natural outline through thin fabric — thick round full ass prominently facing the camera, looking back over her shoulder with a natural playful glance, phone held naturally. Fluorescent gym lighting. Golden sun-kissed Brazilian complexion, lighter warm skin. Natural blue eyes with green center. Brunette hair with natural blonde highlights, loosely pulled back. Soft light freckles. Youthful 19-21, surfer girl aesthetic. Amateur iPhone, not studio. Use the reference image to accurately reproduce her facial features, body shape, proportions, and curves.",
        "filename": "006_mirror_gym_dustyrose_ass.jpg",
        "metadata": {"type": "mirror", "location": "gym"}
    },
    {
        "prompt": "Candid amateur iPhone photo taken by a friend, girl standing at the edge of the tide with water lapping at her feet, wearing a small fitted string bikini — thin fabric with the natural outline of her nipples visible — thick curves, round ass, generous chest. Playful authentic tongue-out expression looking toward the camera, surfer girl energy, hair slightly wind-tousled with natural blonde highlights. Soft warm even beach light, no harsh glare, ocean behind her. Golden sun-kissed Brazilian complexion, lighter warm skin. Natural blue eyes with green center. Soft light freckles. Youthful 19-21. Raw unedited amateur iPhone. Use the reference image to accurately reproduce her facial features, body shape, proportions, and curves.",
        "filename": "007_beach_tide_tongueout.jpg",
        "metadata": {"type": "third-party", "location": "beach"}
    },
    {
        "prompt": "Bathroom mirror selfie, girl wearing a tight bright coral mini skirt and thin white fitted crop top — no bra, subtle natural nipple outline through fabric — thick perfectly round ass prominently facing the camera, looking back over her shoulder with a soft natural expression. Vanity lights, warm glow. Golden sun-kissed Brazilian complexion, lighter warm skin. Natural blue eyes with green center. Brunette hair with natural blonde highlights, loose waves. Soft light freckles. Youthful 19-21, surfer girl aesthetic. Amateur iPhone, not studio. Use the reference image to accurately reproduce her facial features, body shape, proportions, and curves.",
        "filename": "010_mirror_bathroom_coral.jpg",
        "metadata": {"type": "mirror", "location": "bathroom"}
    },
    {
        "prompt": "Overhead bedroom selfie, girl lying back on soft white bedding looking directly up into the camera held above her, frame shows face and decolletage — natural cleavage visible from above, wearing a fitted white scoop-neck crop tee — soft pouty lips slightly parted, sleepy natural expression, no makeup, hair fanned out on the pillow. Warm soft ambient light. Golden sun-kissed Brazilian complexion, lighter warm skin. Natural blue eyes with green center. Brunette hair with natural blonde highlights. Soft light freckles across nose. Youthful 19-21. Raw intimate iPhone aesthetic. Use the reference image to accurately reproduce her facial features, body shape, proportions, and curves.",
        "filename": "011_bed_overhead_pouty.jpg",
        "metadata": {"type": "selfie-overhead", "location": "bedroom"}
    },
    {
        "prompt": "Candid iPhone photo at an upscale coastal restaurant at night, girl at a table near floor-to-ceiling windows with dark ocean waves outside, soft candlelight and dim warm restaurant ambiance, wearing a simple fitted off-shoulder knit top. Natural genuine smile, leaning slightly on the table, relaxed. Golden sun-kissed Brazilian complexion, lighter warm skin. Natural blue eyes with green center. Brunette hair with natural blonde highlights, loose waves. Soft light freckles. Youthful 19-21, surfer girl aesthetic. Authentic dinner candid, amateur iPhone. Use the reference image to accurately reproduce her facial features, body shape, proportions, and curves.",
        "filename": "013_coastal_restaurant_night.jpg",
        "metadata": {"type": "third-party", "location": "coastal restaurant"}
    },
    {
        "prompt": "Candid iPhone photo at a beach bonfire at night, girl crouching near a glowing fire on the sand, warm orange-gold firelight on her face and skin, dark ocean and night sky behind her, wearing a cozy oversized hoodie and denim cutoff shorts, sand between her toes. Natural authentic laugh, eyes alive from the firelight. Golden sun-kissed Brazilian complexion, lighter warm skin. Natural blue eyes with green center. Brunette hair with natural blonde highlights, slightly tousled. Soft light freckles catching the warm glow. Youthful 19-21, surfer girl aesthetic. Raw candid, amateur iPhone. Use the reference image to accurately reproduce her facial features, body shape, proportions, and curves.",
        "filename": "014_beach_bonfire_night.jpg",
        "metadata": {"type": "third-party", "location": "beach bonfire"}
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

import sys, os
sys.path.insert(0, r"C:\Users\pheno\Downloads\wavespeed-batch-api\wavespeed-batch-api")
from wavespeed_client import WaveSpeedClient

API_KEY    = "wsk_live_MWD0E5QYAIV4CP2S3ya2QPZvTApxlw8oBSqPaeLIZ-E"
AVATAR_URL = "https://i.ibb.co/8gd2SqKH/download.jpg"
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR = os.path.join(SCRIPT_DIR, "outputs", "nova_b6")
CHECKPOINT = os.path.join(SCRIPT_DIR, "checkpoint_nova_b6.json")

UNIVERSAL = "Golden sun-kissed Brazilian complexion, lighter warm skin. Natural blue eyes with green center. Sun-kissed brunette hair with natural blonde highlights, slightly wavy beachy texture. Soft light freckles across nose and cheeks. Youthful 19-21, soft natural features. Surfer girl, coastal San Diego lifestyle. Consistent full figure — thick toned legs, round ass, generous chest. Thin fitted clothes, natural fabric. Amateur iPhone quality, natural lens characteristics, slightly imperfect exposure, ambient light inconsistencies. No studio lighting. No iPhone UI frame."

JOBS = [
    {
        "prompt": f"Candid photo taken by a friend, girl sitting at a cafe table reading a book with a coffee cup beside her, wearing a thin fitted ribbed white tank top and denim shorts. Looking down at her book, not aware of the camera, naturally slouched and comfortable. Warm low amber pendant lighting overhead, dark moody cafe interior, slightly underexposed on one side. Arms resting naturally on the table. {UNIVERSAL} Use the reference image to accurately reproduce her facial features, body shape, proportions, and curves.",
        "filename": "001_cafe_reading_ambient.jpg",
        "metadata": {"type": "candid", "location": "cafe"}
    },
    {
        "prompt": f"iPhone selfie at the beach, girl holding phone at arm's length slightly above her, wearing a black triangle bikini top and cutoff denim shorts, bright natural California beach light with slight haze, ocean and white sand behind her. Tongue out playfully looking at the camera, hair blowing slightly from ocean breeze. Natural arm extended selfie angle, slight lens flare from sun, slightly imperfect framing. {UNIVERSAL} Use the reference image to accurately reproduce her facial features, body shape, proportions, and curves.",
        "filename": "002_beach_selfie_tongueout.jpg",
        "metadata": {"type": "selfie", "location": "beach"}
    },
    {
        "prompt": f"Candid beach photo, girl standing on the sand next to her surfboard leaning against her hip, wearing a fitted string bikini in warm earth tones. Relaxed natural expression, golden afternoon California beach light, ocean and waves behind her. Hair slightly wind-tousled, sand on her feet, hand resting on the board. Authentic surfer lifestyle. {UNIVERSAL} Use the reference image to accurately reproduce her facial features, body shape, proportions, and curves.",
        "filename": "003_beach_surfboard.jpg",
        "metadata": {"type": "candid", "location": "beach with surfboard"}
    },
    {
        "prompt": f"Candid photo at Black's Beach in La Jolla San Diego, girl walking naturally along the sand completely nude in broad midday daylight, tall golden sandstone cliffs of Torrey Pines visible in the background, soft natural California coastal light with slight haze, ocean to one side, empty natural beach. Relaxed confident natural posture, genuine authentic expression, no clothing, sun-kissed skin. {UNIVERSAL} Use the reference image to accurately reproduce her facial features, body shape, proportions, and curves.",
        "filename": "004_blacks_beach_nude.jpg",
        "metadata": {"type": "candid", "location": "Blacks Beach San Diego"}
    },
    {
        "prompt": f"iPhone selfie, girl lying on a white bed holding phone in front of her at arm's length, looking directly at the camera with a soft natural expression. Morning window light from one side casting warm shadows across her face and pillow. Close framing showing face and upper chest, wearing a simple thin black fitted crop top. Natural relaxed arms visible at edge of frame. {UNIVERSAL} Use the reference image to accurately reproduce her facial features, body shape, proportions, and curves.",
        "filename": "005_bed_selfie_morning.jpg",
        "metadata": {"type": "selfie", "location": "bedroom"}
    },
    {
        "prompt": f"Candid photo taken by someone at the gym, girl standing near equipment in a thin mauve sports bra and matching high-waist leggings, natural comfortable posture, subtle genuine smile. Fluorescent gym lighting from above with slight shadow variation, gym floor and equipment blurred in background. Arms naturally at sides, full figure visible. {UNIVERSAL} Use the reference image to accurately reproduce her facial features, body shape, proportions, and curves.",
        "filename": "006_gym_candid_mauve.jpg",
        "metadata": {"type": "candid", "location": "gym"}
    },
    {
        "prompt": f"Candid outdoor photo from slightly behind and to the side, girl walking on a San Diego sidewalk near the beach, wearing a white fitted crop tee and a coral tight mini skirt, full round figure prominent. Looking back over her shoulder at the camera with a soft natural expression. Natural slightly overcast daylight, ambient shadow from surrounding environment. {UNIVERSAL} Use the reference image to accurately reproduce her facial features, body shape, proportions, and curves.",
        "filename": "007_outdoor_figure_coral.jpg",
        "metadata": {"type": "candid", "location": "outdoor sidewalk"}
    },
    {
        "prompt": f"Candid photo of girl standing outside on a warm sidewalk, wearing a fitted dark green satin midi dress, natural confident relaxed posture, soft genuine expression. Warm afternoon natural light with slight building shadows. Full figure visible, arms naturally at sides. {UNIVERSAL} Use the reference image to accurately reproduce her facial features, body shape, proportions, and curves.",
        "filename": "008_outdoor_green_dress.jpg",
        "metadata": {"type": "candid", "location": "outdoor"}
    },
    {
        "prompt": f"Candid iPhone photo at an upscale coastal restaurant at night in La Jolla San Diego, girl sitting at a table near large floor-to-ceiling windows with dark ocean waves visible outside. Soft warm candlelight as primary light source, dim ambient restaurant lighting. Wearing a simple thin strappy dress. Natural genuine smile, leaning forward slightly on the table, relaxed and at ease. Warm candlelight with inconsistent soft shadows across her face. Arms resting naturally on the table. {UNIVERSAL} Use the reference image to accurately reproduce her facial features, body shape, proportions, and curves.",
        "filename": "009_restaurant_night_coastal.jpg",
        "metadata": {"type": "candid", "location": "coastal restaurant night"}
    },
    {
        "prompt": f"Candid iPhone photo at a San Diego beach bonfire with a concrete fire ring on the sand, girl sitting naturally near the glowing fire with legs crossed, wearing a thin cotton long-sleeve and denim cutoff shorts, sand on her bare feet. Warm uneven orange-gold firelight illuminating her face and skin from below, dark beach and ocean behind her, night sky above. Natural authentic laugh or smile. Arms resting loosely on her knees. {UNIVERSAL} Use the reference image to accurately reproduce her facial features, body shape, proportions, and curves.",
        "filename": "010_bonfire_concrete_night.jpg",
        "metadata": {"type": "candid", "location": "beach bonfire San Diego"}
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

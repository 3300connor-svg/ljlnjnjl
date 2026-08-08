import sys, os
sys.path.insert(0, r"C:\Users\pheno\Downloads\wavespeed-batch-api\wavespeed-batch-api")
from wavespeed_client import WaveSpeedClient

API_KEY    = "wsk_live_MWD0E5QYAIV4CP2S3ya2QPZvTApxlw8oBSqPaeLIZ-E"
AVATAR_URL = "https://i.ibb.co/L71FBJn/456d6aea768544dc80d45f20084e5d16.png"
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR = os.path.join(SCRIPT_DIR, "outputs", "nova_b2")
CHECKPOINT = os.path.join(SCRIPT_DIR, "checkpoint_nova_b2.json")

JOBS = [
    {
        "prompt": "Candid bedroom selfie, girl in a cropped oversized hoodie with no bra — subtle nipple outline through thin fabric — and tiny black biker shorts showing thick toned legs, sitting on the edge of her bed leaning forward slightly, warm bedside lamp glow, natural relaxed slightly sleepy expression, messy hair. Slightly imperfect framing. Raw, unedited, authentic phone photo. Use the reference image to accurately reproduce her facial features, body shape, proportions, and curves.",
        "filename": "001_selfie_bedroom_hoodie_sexy.jpg",
        "metadata": {"type": "selfie", "location": "bedroom", "outfit": "cropped hoodie+biker shorts"}
    },
    {
        "prompt": "Mirror selfie in a premium modern gym with exposed brick walls and polished equipment, girl in a thin fitted sports bra and high-waist leggings — no bra, subtle nipple outline through fabric — thick toned legs, full round ass, generous chest, phone held naturally at mid-chest with proportionate size visible in reflection, genuine soft smile catching her own eye. Flattering gym lighting. Raw, unedited, authentic social media mirror selfie. Use the reference image to accurately reproduce her facial features, body shape, proportions, and curves.",
        "filename": "002_mirror_gym_premium_smile.jpg",
        "metadata": {"type": "mirror", "location": "premium gym", "outfit": "thin sports bra+leggings"}
    },
    {
        "prompt": "Candid photo taken by a friend at a dimly lit cozy café, girl sitting at a dark wooden table with textbooks and a coffee in front of her, wearing a fitted thin ribbed white tank top with no bra — subtle nipple outline visible through fabric — generous cleavage leaning over her notes, thick toned legs crossed, looking down naturally at her work, low warm amber lighting, moody and atmospheric. Authentic unposed candid. Use the reference image to accurately reproduce her facial features, body shape, proportions, and curves.",
        "filename": "003_cafe_candid_homework_dark.jpg",
        "metadata": {"type": "third-party", "location": "cafe", "outfit": "ribbed white tank"}
    },
    {
        "prompt": "Mirror selfie in a boutique dressing room, girl in a dark emerald green satin bodycon midi dress that hugs every natural curve, soft warm changing room lighting with a full-length mirror, relaxed natural expression like she's genuinely surprised how good it looks — completely unposed, real reaction, hair slightly disheveled from trying things on. Authentic, effortlessly sexy, understated. Raw, unedited mirror selfie. Use the reference image to accurately reproduce her facial features, body shape, proportions, and curves.",
        "filename": "004_mirror_boutique_bodycon_natural.jpg",
        "metadata": {"type": "mirror", "location": "boutique fitting room", "outfit": "emerald satin bodycon"}
    },
    {
        "prompt": "Candid photo taken by the driver while she's in the passenger seat, girl in a low-cut fitted white tee with no bra and generous natural cleavage visible, golden hour light flooding through the window, natural unposed expression looking slightly toward the camera with a relaxed soft smile, thick toned legs, messy wind-blown hair. Authentic candid car photo. Use the reference image to accurately reproduce her facial features, body shape, proportions, and curves.",
        "filename": "005_car_candid_passenger_cleavage.jpg",
        "metadata": {"type": "third-party", "location": "car passenger", "outfit": "low-cut white tee"}
    },
    {
        "prompt": "Mirror selfie at gym, girl in dusty rose thin sports bra and matching high-waist leggings — no bra, nipple outline faintly through fabric — turned so her thick full round ass is prominently facing towards the camera, looking back over her shoulder at the phone with a natural playful glance, phone held naturally, fluorescent gym lighting. Raw, unedited, authentic gym mirror selfie. Use the reference image to accurately reproduce her facial features, body shape, proportions, and curves.",
        "filename": "006_mirror_gym_dustyrose_ass.jpg",
        "metadata": {"type": "mirror", "location": "gym", "outfit": "dusty rose sports bra+leggings"}
    },
    {
        "prompt": "Authentic amateur beach photo, girl in a bright colorful string bikini top and matching bikini bottoms showing full curves and thick toned legs, standing ankle-deep in the ocean, soft warm overcast light with no harsh sun glare, genuine mid-laugh expression like someone just said something funny off camera, eyes alive and bright, hair naturally tousled and slightly wet from the water. Spontaneous, joyful, real. Raw, unedited authentic beach photo. Use the reference image to accurately reproduce her facial features, body shape, proportions, and curves.",
        "filename": "007_beach_bikini_alive_laughing.jpg",
        "metadata": {"type": "third-party", "location": "beach", "outfit": "colorful string bikini"}
    },
    {
        "prompt": "Bedroom mirror selfie, girl in a thin champagne silk slip dress — no bra, faint nipple outline through silk — turned three-quarters so her thick full round ass is prominent and faces the mirror, looking back over her shoulder at the camera with a soft natural pouty expression, warm lamp light on her skin, unmade bed visible in background. Raw, unedited, authentic social media mirror selfie. Use the reference image to accurately reproduce her facial features, body shape, proportions, and curves.",
        "filename": "008_mirror_bedroom_slipDress_ass.jpg",
        "metadata": {"type": "mirror", "location": "bedroom", "outfit": "champagne silk slip dress"}
    },
    {
        "prompt": "Candid photo from behind at a Wendy's fast food restaurant, girl standing in line with her thick full round ass prominent in tight fitted jeans, casual fitted cropped top, bright warm fast food interior lighting, natural unposed stance like she has no idea the photo is being taken, people and menu boards visible in background. Authentic caught-off-guard social candid. Use the reference image to accurately reproduce her facial features, body shape, proportions, and curves.",
        "filename": "009_wendys_candid_ass_inline.jpg",
        "metadata": {"type": "third-party-behind", "location": "Wendy's", "outfit": "tight jeans+cropped top"}
    },
    {
        "prompt": "Bathroom mirror selfie, girl wearing a tight bright coral form-fitting mini skirt and a thin cropped white top — no bra, subtle nipple outline through fabric — turned so her thick perfectly round ass is facing directly toward the camera, big and prominent yet naturally proportionate, looking back over her shoulder at the mirror with a soft natural expression, vanity lights casting warm glow. Raw, unedited, authentic social media mirror selfie. Use the reference image to accurately reproduce her facial features, body shape, proportions, and curves.",
        "filename": "010_mirror_bathroom_coral_ass.jpg",
        "metadata": {"type": "mirror", "location": "bathroom", "outfit": "coral mini skirt+white crop top"}
    },
    {
        "prompt": "Pinterest-style bedroom selfie, girl laying face-down on a soft white bed looking straight into the camera, natural puffed pouty lips, soft sleepy eyes with no makeup, messy hair spread naturally around her, wearing a low-cut crop top with generous cleavage resting against the sheets, soft warm morning window light streaming in from the side, clean aesthetic, intimate and genuine expression. Raw, authentic, cozy. Use the reference image to accurately reproduce her facial features, body shape, proportions, and curves.",
        "filename": "011_pinterest_bed_selfie_cleavage.jpg",
        "metadata": {"type": "selfie", "location": "bedroom", "outfit": "low-cut crop top"}
    },
    {
        "prompt": "Selfie in the driver's seat at night, girl with heavy tired eyes and a subtle exhausted soft expression, dim phone screen glow as the only light source illuminating her face from below, dark car interior, night visible through the windshield, hair slightly messy, no makeup, no bra under a loose top, the kind of photo you take after a long day before you go inside. Raw, unedited, authentic late-night phone selfie. Use the reference image to accurately reproduce her facial features, body shape, proportions, and curves.",
        "filename": "012_selfie_car_night_tired.jpg",
        "metadata": {"type": "selfie", "location": "car night", "outfit": "loose top no bra"}
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

import sys, os
sys.path.insert(0, r"C:\Users\pheno\Downloads\wavespeed-batch-api\wavespeed-batch-api")
from wavespeed_client import WaveSpeedClient

API_KEY    = "wsk_live_MWD0E5QYAIV4CP2S3ya2QPZvTApxlw8oBSqPaeLIZ-E"
AVATAR_URL = "https://i.ibb.co/L71FBJn/456d6aea768544dc80d45f20084e5d16.png"
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR = os.path.join(SCRIPT_DIR, "outputs", "nova_b1")
CHECKPOINT = os.path.join(SCRIPT_DIR, "checkpoint_nova_b1.json")

JOBS = [
    {
        "prompt": "Amateur iPhone 14 selfie, arm extended at slight upward angle, lip bite expression, wearing oversized hoodie and biker shorts, cozy bedroom with fairy lights in background, warm bedroom lamp light. Flyaway hair strand across cheek, slight motion blur at edge. Raw, unedited, spontaneous. Slightly imperfect framing, arm partially visible at bottom edge. Use the reference image to accurately reproduce her facial features, body shape, proportions, and curves.",
        "filename": "001_selfie_bedroom_hoodie_lipbite.jpg",
        "metadata": {"type": "selfie", "location": "bedroom", "outfit": "hoodie+biker shorts", "emotion": "lip bite"}
    },
    {
        "prompt": "Mirror selfie taken with iPhone 14, post-workout pose, full sports bra and high-waist leggings outfit, gym locker room with white tile walls, harsh fluorescent gym lighting. Phone held at chest level, smirk expression. Full-length gym mirror reflection visible. Phone reflection in mirror, hair slightly messy from workout. Raw, unedited, authentic social media mirror selfie aesthetic. Use the reference image to accurately reproduce her facial features, body shape, proportions, and curves.",
        "filename": "002_mirror_gym_sportsbra_smirk.jpg",
        "metadata": {"type": "mirror", "location": "gym", "outfit": "sports bra+leggings", "emotion": "smirk"}
    },
    {
        "prompt": "Amateur iPhone 12 selfie, eye-level angle, puffed cheeks expression, wearing linen co-ord set in beige, cozy café with wooden tables and hanging plants in background, soft diffused cloudy daylight through large window. Finger partially blocking corner, uneven lighting from window. Raw, unedited, spontaneous. Slightly imperfect framing, arm partially visible at bottom edge. Use the reference image to accurately reproduce her facial features, body shape, proportions, and curves.",
        "filename": "003_selfie_cafe_linen_puffedcheeks.jpg",
        "metadata": {"type": "selfie", "location": "cafe", "outfit": "linen co-ord", "emotion": "puffed cheeks"}
    },
    {
        "prompt": "Mirror selfie taken with iPhone 14, standing and turning slightly to show full outfit, bodycon mini dress in dark green, mall changing room with white curtains and warm overhead light. Phone held at waist level, raised brow and playful look. Full-length changing room mirror reflection. Minor lens smudge, slight overexposure on one side. Raw, unedited, authentic social media mirror selfie aesthetic. Use the reference image to accurately reproduce her facial features, body shape, proportions, and curves.",
        "filename": "004_mirror_mall_bodycon_raisedbrow.jpg",
        "metadata": {"type": "mirror", "location": "mall", "outfit": "bodycon mini dress", "emotion": "raised brow"}
    },
    {
        "prompt": "Amateur iPhone 14 selfie, low angle from passenger seat, closed-eye grin, wearing fitted white tee and light-wash jeans, car interior with highway blurred through window, golden hour window light pouring in. Flyaway hair strand across cheek, slight overexposure on one side. Raw, unedited, spontaneous. Slightly imperfect framing, arm partially visible at bottom edge. Use the reference image to accurately reproduce her facial features, body shape, proportions, and curves.",
        "filename": "005_selfie_car_whitetee_closedeyegrin.jpg",
        "metadata": {"type": "selfie", "location": "car", "outfit": "white tee+jeans", "emotion": "closed-eye grin"}
    },
    {
        "prompt": "Mirror selfie taken with iPhone 12, full-body pose with hip cocked slightly, matching sports bra and high-waist leggings in dusty rose, gym with rubber floors and equipment visible in background, fluorescent gym lighting. Phone held at chest level, playful squint expression. Full gym mirror reflection. Phone reflection visible in mirror, hair tied up messy. Raw, unedited, authentic social media mirror selfie aesthetic. Use the reference image to accurately reproduce her facial features, body shape, proportions, and curves.",
        "filename": "006_mirror_gym_dustyrose_playfulsquint.jpg",
        "metadata": {"type": "mirror", "location": "gym", "outfit": "sports bra+leggings dusty rose", "emotion": "playful squint"}
    },
    {
        "prompt": "Amateur iPhone 14 selfie, arm extended slightly downward, tongue out expression, wearing string bikini top and cutoff denim shorts, beach with ocean and white sand in background, harsh direct summer sunlight. Slight motion blur at edge, minor lens smudge from sun glare. Raw, unedited, spontaneous. Slightly imperfect framing, arm partially visible at bottom edge. Use the reference image to accurately reproduce her facial features, body shape, proportions, and curves.",
        "filename": "007_selfie_beach_bikini_tongueout.jpg",
        "metadata": {"type": "selfie", "location": "beach", "outfit": "bikini top+denim shorts", "emotion": "tongue out"}
    },
    {
        "prompt": "Mirror selfie taken with iPhone 14, full-length pose with slight lean against wall, silk slip dress in champagne color, bedroom with unmade bed and soft lamp visible in background, warm bedroom lamp light. Phone held at chest level, pouty face expression. Full bedroom mirror with decorative frame visible in reflection. Flyaway hair strand visible, slight overexposure from lamp on one side. Raw, unedited, authentic social media mirror selfie aesthetic. Use the reference image to accurately reproduce her facial features, body shape, proportions, and curves.",
        "filename": "008_mirror_bedroom_slipDress_pouty.jpg",
        "metadata": {"type": "mirror", "location": "bedroom", "outfit": "silk slip dress", "emotion": "pouty face"}
    },
    {
        "prompt": "Amateur iPhone 12 selfie, slightly upward angle, surprised O-mouth expression, wearing fitted crop blazer and matching tailored trousers in camel, busy city sidewalk with blurred storefronts behind, soft diffused cloudy daylight. Slight motion blur at edge, uneven lighting from surrounding buildings. Raw, unedited, spontaneous. Slightly imperfect framing, arm partially visible at bottom edge. Use the reference image to accurately reproduce her facial features, body shape, proportions, and curves.",
        "filename": "009_selfie_street_blazer_surprisedO.jpg",
        "metadata": {"type": "selfie", "location": "city street", "outfit": "crop blazer+trousers", "emotion": "surprised O-mouth"}
    },
    {
        "prompt": "Mirror selfie taken with iPhone 14, three-quarter pose showing full outfit, strappy black going-out top and fitted dark jeans, bathroom with marble counter and vanity lights, harsh overhead bathroom light. Phone held at waist level, shy glance down with soft smile. Full bathroom mirror reflection with vanity lights visible. Phone reflection in mirror, hair slightly mussed. Raw, unedited, authentic social media mirror selfie aesthetic. Use the reference image to accurately reproduce her facial features, body shape, proportions, and curves.",
        "filename": "010_mirror_bathroom_strapTop_shyglance.jpg",
        "metadata": {"type": "mirror", "location": "bathroom", "outfit": "strappy top+dark jeans", "emotion": "shy glance down"}
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

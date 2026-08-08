import sys, os
sys.path.insert(0, r"C:\Users\pheno\Downloads\wavespeed-batch-api\wavespeed-batch-api")
from wavespeed_client import WaveSpeedClient

API_KEY    = "wsk_live_MWD0E5QYAIV4CP2S3ya2QPZvTApxlw8oBSqPaeLIZ-E"
AVATAR_URL = "https://i.ibb.co/8gd2SqKH/download.jpg"
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR = os.path.join(SCRIPT_DIR, "outputs", "nova_b6_three")
CHECKPOINT = os.path.join(SCRIPT_DIR, "checkpoint_nova_b6_three.json")

UNIVERSAL = "Golden sun-kissed Brazilian complexion, lighter warm skin. Natural blue eyes with green center. Sun-kissed brunette hair with natural blonde highlights. Soft light freckles across nose and cheeks. Youthful 19-21, surfer girl, coastal San Diego. Consistent full figure — thick toned legs, round prominent ass, generous full chest. No studio lighting, no artificial glow. Natural flat ambient light, slightly imperfect exposure, muted warm tones, noisy image, natural skin texture. Use the reference image to accurately reproduce her facial features, body shape, proportions, and curves."

JOBS = [
    {
        "prompt": f"Candid photo shot from directly behind, close up, at Black's Beach San Diego. Girl completely nude, legs shoulder-width apart, bent forward at the waist reaching down to grab her surfboard off the sand with both hands. Facing away from camera completely — back of head visible, wet salty hair hanging forward. Bent over posture naturally opens her stance wide, full figure exposed from behind. Camera low, tight behind framing. Sandstone Torrey Pines cliffs in background. Genuinely mid-action, unposed, not aware of camera. Flat muted coastal afternoon light, no cinematic glow, natural haze, real outdoor ambient. {UNIVERSAL}",
        "filename": "006_blacks_beach_bend_board.jpg",
        "metadata": {"type": "candid-behind-bend", "location": "Blacks Beach surfboard pickup"}
    },
    {
        "prompt": f"Candid photo at Black's Beach San Diego. Girl lying face-down on the sand, completely nude, upper body propped up on her elbows, full chest resting and pressing into the warm sand, looking directly up at the camera with a natural relaxed smile. Ass raised slightly in the air behind her. Camera angled down toward her face close and personal. Wet salty hair falling around her face and onto the sand. Warm muted afternoon coastal light, flat ambient, no dramatic highlights, slightly noisy exposure, imperfect focus edges. Genuinely in the moment. Sandstone cliffs and ocean in background. {UNIVERSAL}",
        "filename": "007_blacks_beach_prone_smile.jpg",
        "metadata": {"type": "candid-prone-smile", "location": "Blacks Beach prone smile"}
    },
    {
        "prompt": f"Candid photo from directly behind at Black's Beach San Diego. Girl completely nude, lying face-down on the sand, ass raised naturally in the air, legs slightly apart. Camera positioned directly behind her at low angle, tight framing on her from behind, full figure exposed. She is not looking at the camera — facing forward toward the ocean. Wet salty hair visible. Warm muted flat coastal afternoon light, no cinematic glow, natural outdoor ambient, slightly imperfect exposure, muted color tones, noisy image. Torrey Pines sandstone cliffs in background. Unposed, genuinely in the moment. {UNIVERSAL}",
        "filename": "008_blacks_beach_prone_behind.jpg",
        "metadata": {"type": "candid-prone-behind", "location": "Blacks Beach prone from behind"}
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
    max_concurrent=3,
    progress_callback=progress,
    checkpoint_path=CHECKPOINT,
)
print(f"Done: {result['n_success']}/{result['n_total']} | Failed: {result['n_failed']} | {result['duration_s']:.0f}s")

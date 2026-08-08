import sys, os
sys.path.insert(0, r"C:\Users\pheno\Downloads\wavespeed-batch-api\wavespeed-batch-api")
from wavespeed_client import WaveSpeedClient

API_KEY    = "wsk_live_MWD0E5QYAIV4CP2S3ya2QPZvTApxlw8oBSqPaeLIZ-E"
AVATAR_URL = "https://i.ibb.co/8gd2SqKH/download.jpg"
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR = os.path.join(SCRIPT_DIR, "outputs", "nova_b6_three_v2")
CHECKPOINT = os.path.join(SCRIPT_DIR, "checkpoint_nova_b6_three_v2.json")

UNIVERSAL = "Golden sun-kissed Brazilian complexion, lighter warm skin. Natural blue eyes with green center. Sun-kissed brunette hair with natural blonde highlights. Soft light freckles across nose and cheeks. Youthful 19-21, surfer girl, coastal San Diego. Consistent full figure — thick toned legs, round prominent ass, generous full chest. Use the reference image to accurately reproduce her facial features, body shape, proportions, and curves."

LIGHT = "Direct afternoon coastal sun at low angle casting hard natural shadows across her body and face, deep defined shadow contrast, uneven light patches and hot spots on skin, partial shadow across her face from sun angle, natural lighting imperfections, no artificial fill light, no softbox glow. Sharp image, crisp natural detail, no blur, no soft focus."

JOBS = [
    {
        "prompt": f"Candid photo shot from directly behind at Black's Beach San Diego, close low camera angle tight on her form. Girl completely nude, legs planted wide apart, deeply bent forward at the waist both hands reaching down gripping her surfboard on the sand. Back of her head facing camera, head down, wet salty hair hanging forward — not looking at camera at all. Wide stance with legs apart exposes full anatomy between her legs naturally from this angle. Camera directly behind her, low, tight framing. Genuinely mid-action catching her off guard. Sandstone Torrey Pines cliffs in background. {LIGHT} {UNIVERSAL}",
        "filename": "006_blacks_beach_bend_board_v2.jpg",
        "metadata": {"type": "candid-behind-bend-v2"}
    },
    {
        "prompt": f"Candid photo at Black's Beach San Diego. Girl completely nude lying face-down on the sand, upper body fully raised up on both hands with arms straight, back deeply arched downward, hips and ass raised high in the air behind her, full chest and breasts hanging naturally downward with gravity away from her body, not touching the sand. Looking directly up at the camera with a relaxed natural smile, genuine not posed. Camera angled down close to her face. Wet salty hair hanging around her face. Legs slightly apart, ass prominently elevated. Genuinely in the moment. Sandstone cliffs and ocean in background. {LIGHT} {UNIVERSAL}",
        "filename": "007_blacks_beach_prone_smile_v2.jpg",
        "metadata": {"type": "candid-prone-smile-v2"}
    },
    {
        "prompt": f"Candid photo from directly behind at Black's Beach San Diego, low camera angle. Girl completely nude, face-down on sand, upper body raised on straight arms, back deeply arched, ass raised prominently high in the air, legs slightly apart. Camera directly behind her at low angle showing full form from behind with legs parted, full anatomy between legs visible naturally from this angle. She is facing away from camera entirely toward the ocean — not looking back. Wet salty hair visible. Tight close framing from behind. Genuinely unaware of camera, unposed. Torrey Pines cliffs in background. {LIGHT} {UNIVERSAL}",
        "filename": "008_blacks_beach_prone_behind_v2.jpg",
        "metadata": {"type": "candid-prone-behind-v2"}
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

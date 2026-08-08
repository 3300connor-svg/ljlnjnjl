import os
import numpy as np
from PIL import Image, ImageFilter

FOLDER = r"C:\Users\pheno\Downloads\wavespeed-batch-api\outputs\nova_b6"
JPEG_QUALITY = 65
GRAIN_AMOUNT = 7

def process(path):
    img = Image.open(path).convert("RGB")

    # Unsharp mask — sharpen edges, skip smooth skin (threshold=8)
    img = img.filter(ImageFilter.UnsharpMask(radius=0.6, percent=60, threshold=8))

    # Film grain — monochromatic noise via luminance channel
    arr = np.array(img, dtype=np.float32)
    noise = np.random.normal(0, GRAIN_AMOUNT, arr.shape[:2])  # single channel
    for c in range(3):
        arr[:, :, c] = np.clip(arr[:, :, c] + noise, 0, 255)
    img = Image.fromarray(arr.astype(np.uint8))

    # Save in-place as JPEG at 68% quality
    img.save(path, "JPEG", quality=JPEG_QUALITY, optimize=True)
    print(f"done: {os.path.basename(path)}")

files = [f for f in os.listdir(FOLDER) if f.lower().endswith(".jpg")]
print(f"Processing {len(files)} images...")
for f in files:
    process(os.path.join(FOLDER, f))
print("All done.")

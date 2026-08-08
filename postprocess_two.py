import os, numpy as np
from PIL import Image, ImageFilter

FOLDER = r"C:\Users\pheno\Downloads\wavespeed-batch-api\outputs\nova_b6"
FILES = ["002_beach_selfie_tongueout_v2.jpg", "004_blacks_beach_nude_v2.jpg"]

for fname in FILES:
    path = os.path.join(FOLDER, fname)
    img = Image.open(path).convert("RGB")
    img = img.filter(ImageFilter.UnsharpMask(radius=0.6, percent=60, threshold=8))
    arr = np.array(img, dtype=np.float32)
    noise = np.random.normal(0, 7, arr.shape[:2])
    for c in range(3):
        arr[:, :, c] = np.clip(arr[:, :, c] + noise, 0, 255)
    Image.fromarray(arr.astype(np.uint8)).save(path, "JPEG", quality=65, optimize=True)
    print(f"done: {fname}")

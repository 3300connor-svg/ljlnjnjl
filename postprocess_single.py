import os, numpy as np
from PIL import Image, ImageFilter

PATH = r"C:\Users\pheno\Downloads\wavespeed-batch-api\outputs\nova_b4\008_mirror_bedroom_slip_forward.jpg"

img = Image.open(PATH).convert("RGB")
img = img.filter(ImageFilter.UnsharpMask(radius=0.6, percent=60, threshold=8))
arr = np.array(img, dtype=np.float32)
noise = np.random.normal(0, 12, arr.shape[:2])
for c in range(3):
    arr[:, :, c] = np.clip(arr[:, :, c] + noise, 0, 255)
Image.fromarray(arr.astype(np.uint8)).save(PATH, "JPEG", quality=65, optimize=True)
print("done")

"""
run_single.py — Run the full video pipeline on one URL.
Usage: py run_single.py <video_url>
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from pipeline import run_pipeline

if len(sys.argv) < 2:
    print("Usage: py run_single.py <video_url>")
    sys.exit(1)

url = sys.argv[1]
print(f"Starting pipeline for: {url}\n")
result = run_pipeline(url, progress_cb=lambda m: print(f"  {m}"))

if result:
    print(f"\nDone: {result}")
else:
    print("\nPipeline failed.")
    sys.exit(1)

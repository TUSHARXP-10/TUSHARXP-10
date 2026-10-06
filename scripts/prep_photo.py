"""Turn your own photo into the ASCII portrait (run locally, once per photo).

  pip install -r scripts/requirements.txt
  python scripts/prep_photo.py path/to/photo.jpg

1. Remove the background (rembg) so only you are left.
2. Boost local contrast with CLAHE so a flatly lit face gets real shadows.
3. Composite onto white so the background prints as spaces.
4. Save only the ASCII rows to data/portrait.json (source: "photo"); the
   photo itself never enters the repo. Commit that file and push.

To go back to the auto-updating GitHub-avatar portrait, delete data/portrait.json.
"""
import sys
from pathlib import Path

import cv2
import numpy as np
from PIL import Image, ImageOps

from card_portrait import grid_from_image, write_cache


def main():
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    img = ImageOps.exif_transpose(Image.open(Path(sys.argv[1]))).convert("RGBA")
    try:
        from rembg import remove
        img = remove(img)
    except ImportError:
        print("rembg not installed; keeping the original background")

    alpha = np.asarray(img.getchannel("A"), dtype=np.float32) / 255
    gray = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8)).apply(np.asarray(img.convert("L")))
    out = gray.astype(np.float32) * alpha + 255 * (1 - alpha)

    ys, xs = np.where(alpha > 0.1)  # crop to the subject, with a small margin
    if len(xs):
        m = int(0.04 * max(out.shape))
        out = out[max(ys.min() - m, 0):ys.max() + m, max(xs.min() - m, 0):xs.max() + m]

    rows = grid_from_image(Image.fromarray(out.clip(0, 255).astype(np.uint8), "L"))
    write_cache(rows, "photo")
    print(f"wrote data/portrait.json ({len(rows)} rows) — run python scripts/build.py, then commit")


if __name__ == "__main__":
    main()

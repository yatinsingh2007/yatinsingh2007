#!/usr/bin/env python3
"""
Prep a photo for ASCII conversion:
  1. Remove the background (rembg) so only the subject remains.
  2. Boost local contrast with CLAHE so a flat face gets real
     highlights/shadows (otherwise it converts to a dark blob).
  3. Composite onto pure white, so the background maps to the blank
     end of the ASCII ramp (white -> space).

Usage:
    python scripts/prep_photo.py source-photo.jpg
Writes:
    scripts/prepped.png  (grayscale)
"""
import sys
import os

import cv2
import numpy as np
from PIL import Image
from rembg import remove

OUT_PATH = os.path.join(os.path.dirname(__file__), "prepped.png")


def remove_background(img_bytes: bytes) -> Image.Image:
    result = remove(img_bytes)
    return Image.open(__import__("io").BytesIO(result)).convert("RGBA")


def apply_clahe(gray: np.ndarray) -> np.ndarray:
    clahe = cv2.createCLAHE(clipLimit=2.5, tileGridSize=(8, 8))
    return clahe.apply(gray)


def composite_on_white(rgba: Image.Image) -> Image.Image:
    white_bg = Image.new("RGBA", rgba.size, (255, 255, 255, 255))
    return Image.alpha_composite(white_bg, rgba)


def main():
    if len(sys.argv) != 2:
        print("Usage: python prep_photo.py <source-photo.jpg>", file=sys.stderr)
        sys.exit(1)

    src_path = sys.argv[1]
    with open(src_path, "rb") as f:
        img_bytes = f.read()

    print("[prep_photo] removing background...")
    no_bg = remove_background(img_bytes)

    print("[prep_photo] compositing on white...")
    on_white = composite_on_white(no_bg).convert("RGB")

    print("[prep_photo] boosting local contrast (CLAHE)...")
    cv_img = cv2.cvtColor(np.array(on_white), cv2.COLOR_RGB2GRAY)
    contrasted = apply_clahe(cv_img)

    out_img = Image.fromarray(contrasted)
    out_img.save(OUT_PATH)
    print(f"[prep_photo] wrote {OUT_PATH} ({out_img.size[0]}x{out_img.size[1]})")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""XOR two images pixel-by-pixel to reveal hidden data."""

from PIL import Image
import numpy as np

img_flag = np.array(Image.open("./flag.png"))
img_lemur = np.array(Image.open("./lemur.png"))

# Verify dimensions match
if img_flag.shape != img_lemur.shape:
    print("Kernel Panic: Image dimensions do not match!")
    exit(1)

result_matrix = np.bitwise_xor(img_flag, img_lemur)
Image.fromarray(result_matrix).save("./result.png")

print("XOR complete.")

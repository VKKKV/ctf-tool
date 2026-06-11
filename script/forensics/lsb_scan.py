#!/usr/bin/env python3
"""
lsb_scan.py — 遍历 PNG 所有 bit plane，输出各通道各 bit 的图像。

用法:
  uv run python3 lsb_scan.py <input.png> [output_dir]

输出:
  <output_dir>/bit{N}_{R|G|B}.png  (默认 output_dir = lsb_planes/)
"""

import sys, os
from PIL import Image

def main():
    if len(sys.argv) < 2:
        print(f"Usage: {sys.argv[0]} <input.png> [output_dir]", file=sys.stderr)
        sys.exit(1)

    img_path = sys.argv[1]
    out_dir = sys.argv[2] if len(sys.argv) > 2 else 'lsb_planes'

    img = Image.open(img_path)
    if img.mode != 'RGB':
        img = img.convert('RGB')

    w, h = img.size
    pixels = list(img.getdata())
    os.makedirs(out_dir, exist_ok=True)

    channels = {'R': 0, 'G': 1, 'B': 2}

    for bit in range(8):
        for c_name, c_idx in channels.items():
            out = Image.new('L', (w, h))
            out_pixels = []
            for pixel in pixels:
                val = (pixel[c_idx] >> bit) & 1
                out_pixels.append(255 if val else 0)
            out.putdata(out_pixels)
            path = os.path.join(out_dir, f'bit{bit}_{c_name}.png')
            out.save(path)

    # Print summary: for each channel, find the bit with most extreme ratio
    # (hidden text usually appears as very sparse white pixels on black bg)
    print(f"Output: {out_dir}/")
    print(f"Image: {w}x{h} {len(pixels)} pixels")
    print()
    print("Channel  | bit | white% | note")
    print("---------|-----|--------|------")
    for c_name, c_idx in channels.items():
        for bit in range(8):
            total = len(pixels)
            white = sum(1 for p in pixels if ((p[c_idx] >> bit) & 1))
            pct = white / total * 100
            note = ""
            if pct < 5:
                note = " <-- sparse (likely text)"
            elif pct > 95:
                note = " <-- sparse inverted"
            elif 40 <= pct <= 60:
                note = " (noise-like)"
            if note:
                print(f"  {c_name}     |  {bit}  | {pct:5.1f}% |{note}")

if __name__ == '__main__':
    main()

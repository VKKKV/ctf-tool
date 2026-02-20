#!/usr/bin/env python3
"""
Image Byte Manipulation Script
Corrects images where bytes have been inverted/transformed (0x100 - byte).
"""

import os
import sys

def process_image(input_path, output_path):
    if not os.path.exists(input_path):
        print(f"Error: {input_path} not found.")
        return

    print(f"[*] Processing {input_path} -> {output_path}...")
    try:
        with open(input_path, "rb") as f:
            data = f.read()

        # Transformation: If byte is 0, keep 0. Otherwise 256 - value.
        # This looks like a simple complement/inversion variant.
        processed = bytearray()
        for b in data:
            if b == 0:
                processed.append(0)
            else:
                processed.append((0x100 - b) & 0xFF)

        with open(output_path, "wb") as f:
            f.write(processed)
        print("[+] Done.")
    except Exception as e:
        print(f"[!] Error: {e}")

if __name__ == "__main__":
    infile = "打不开的图/misc5.5.png"
    outfile = "./output.png"
    
    if len(sys.argv) > 2:
        infile, outfile = sys.argv[1], sys.argv[2]
        
    process_image(infile, outfile)

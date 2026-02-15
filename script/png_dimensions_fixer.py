#!/usr/bin/env python3
"""
PNG Dimensions Fixer
Brute-forces both Width and Height of a PNG file using its IHDR CRC32.
"""

import zlib
import struct
import sys
import os

def fix_png_dimensions(file_path, target_crc=None):
    if not os.path.exists(file_path):
        print(f"Error: {file_path} not found.")
        return

    with open(file_path, "rb") as f:
        raw_data = f.read()

    # IHDR chunk starts at offset 12 (after 8-byte PNG header and 4-byte chunk length)
    # The data used for CRC starts at offset 12 and is 17 bytes long ('IHDR' + 13 bytes data)
    ihdr_data = bytearray(raw_data[12:29])
    
    # If target_crc is not provided, read it from the file (offsets 29-33)
    if target_crc is None:
        target_crc = struct.unpack(">I", raw_data[29:33])[0]
    
    print(f"[*] Target CRC: {hex(target_crc)}")
    print("[*] Brute-forcing dimensions (0-4095)...")

    limit = 4096
    for w in range(limit):
        width_bytes = struct.pack(">I", w)
        for h in range(limit):
            height_bytes = struct.pack(">I", h)
            
            # Update width and height in IHDR data (offsets 4-8 and 8-12 relative to 'IHDR')
            ihdr_data[4:8] = width_bytes
            ihdr_data[8:12] = height_bytes
            
            if zlib.crc32(ihdr_data) & 0xFFFFFFFF == target_crc:
                print(f"\n[+] SUCCESS! Found dimensions: {w}x{h}")
                
                # Create the fixed image data
                new_data = bytearray(raw_data)
                # PNG uses big-endian for IHDR width/height
                # Original offsets in file: 16-20 (Width), 20-24 (Height)
                new_data[16:20] = width_bytes
                new_data[20:24] = height_bytes
                
                output_path = file_path.replace(".png", "_fixed.png")
                with open(output_path, "wb") as f:
                    f.write(new_data)
                
                print(f"[+] Fixed image saved to: {output_path}")
                return

        if w % 100 == 0:
            sys.stdout.write(f"\r[*] Progress: {w}/{limit}...")
            sys.stdout.flush()

    print("\n[-] Failed to find matching dimensions.")

if __name__ == "__main__":
    target_file = "./miku/miku.png"
    if len(sys.argv) > 1:
        target_file = sys.argv[1]
    
    # You can also manually specify a CRC if the file's CRC is corrupted
    # fix_png_dimensions(target_file, 0x7507B944)
    fix_png_dimensions(target_file)

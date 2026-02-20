#!/usr/bin/env python3
"""
PNG Forensics Toolkit
Utilities for fixing dimensions, brute-forcing CRCs, and basic zlib operations.
"""

import binascii
import struct
import zlib
import os
import sys

def fix_png_dimensions(file_path, target_crc=None):
    """Brute-forces both Width and Height of a PNG file using its IHDR CRC32."""
    if not os.path.exists(file_path):
        print(f"Error: {file_path} not found.")
        return

    with open(file_path, "rb") as f:
        raw_data = f.read()

    # IHDR chunk starts after 8-byte PNG header and 4-byte chunk length
    ihdr_data = bytearray(raw_data[12:29])
    
    if target_crc is None:
        target_crc = struct.unpack(">I", raw_data[29:33])[0]
    
    print(f"[*] Target CRC: {hex(target_crc)}")
    print("[*] Brute-forcing dimensions (up to 4096px)...")

    for w in range(4096):
        width_bytes = struct.pack(">I", w)
        for h in range(4096):
            height_bytes = struct.pack(">I", h)
            ihdr_data[4:8] = width_bytes
            ihdr_data[8:12] = height_bytes
            
            if zlib.crc32(ihdr_data) & 0xFFFFFFFF == target_crc:
                print(f"
[+] SUCCESS! Found dimensions: {w}x{h}")
                new_data = bytearray(raw_data)
                new_data[16:20] = width_bytes
                new_data[20:24] = height_bytes
                
                output_path = file_path.replace(".png", "_fixed.png")
                with open(output_path, "wb") as f:
                    f.write(new_data)
                print(f"[+] Fixed image saved to: {output_path}")
                return

        if w % 100 == 0:
            sys.stdout.write(f"[*] Progress: {w}/4096...")
            sys.stdout.flush()
    print("
[-] Failed to find matching dimensions.")

def brute_force_png_height(file_path, target_crc):
    """Brute force ONLY PNG height (faster if width is known)."""
    with open(file_path, "rb") as f:
        data = f.read()
    
    print(f"[*] Brute-forcing height for {file_path} (Target CRC: {hex(target_crc)})...")
    for i in range(4096):
        # 'IHDR' (4) + Width (4) + Height (4) + ...
        ihdr_part = data[12:16] + struct.pack(">I", i) + data[20:29]
        if binascii.crc32(ihdr_part) & 0xFFFFFFFF == target_crc:
            print(f"[+] Found correct height: {i} (0x{i:x})")
            return i
    print("[-] Height not found.")

def decompress_zlib(input_path, output_path):
    """Decompress zlib data extracted from a file."""
    try:
        with open(input_path, "rb") as f:
            data = f.read()
        decompressed = zlib.decompress(data)
        with open(output_path, "wb") as f:
            f.write(decompressed)
        print(f"[+] Decompressed {input_path} to {output_path}")
    except Exception as e:
        print(f"[!] Zlib error: {e}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: png_utils.py <file_path> [target_crc]")
        sys.exit(1)
    
    path = sys.argv[1]
    crc = int(sys.argv[2], 16) if len(sys.argv) > 2 else None
    fix_png_dimensions(path, crc)

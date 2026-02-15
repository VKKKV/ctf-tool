#!/usr/bin/env python3
"""
Image Forensics Toolkit
Contains utilities for PNG CRC brute-forcing, zlib decompression, and password list generation.
"""

import binascii
import struct
import zlib
import os

def brute_force_png_height(file_path, target_crc):
    """Brute force PNG height to match a given CRC32 (common in CTF)."""
    if not os.path.exists(file_path):
        print(f"Error: {file_path} not found.")
        return

    with open(file_path, "rb") as f:
        misc = f.read()

    print(f"[*] Brute-forcing height for {file_path} (Target CRC: {hex(target_crc)})...")
    # IHDR chunk: Length (4) + 'IHDR' (4) + Width (4) + Height (4) + bit depth/color type/etc (5)
    # data part for CRC: 'IHDR' + Width + Height + bit depth...
    for i in range(2000): # Check up to 2000px height
        data = misc[12:16] + struct.pack(">i", i) + misc[20:29]
        crc32 = binascii.crc32(data) & 0xFFFFFFFF
        if crc32 == target_crc:
            print(f"[+] Found correct height: {i} (0x{i:x})")
            return i
    print("[-] Height not found in range.")

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

def generate_password_list(output_path, prefix="372", length=6):
    """Generate a password list with a fixed prefix and sequential suffix."""
    print(f"[*] Generating password list to {output_path}...")
    with open(output_path, "w") as f:
        for i in range(10**length):
            password = prefix + str(i).zfill(length)
            f.write(password + "\n")
    print(f"[+] Generated {10**length} passwords.")

if __name__ == "__main__":
    # Example usage (commented out or customized by user)
    # brute_force_png_height("miku/miku.png", 0x3581D104)
    pass

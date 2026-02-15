#!/usr/bin/env python3
"""
Data Conversion Utility
Converts a list of decimal ASCII values to various formats (Hex, String, Base64).
"""

import base64

# Original data from the script
DATA = [86, 71, 57, 107, 89, 88, 107, 103, 97, 88, 77, 103, 89, 83, 66, 110, 98, 50, 57, 107, 73, 71, 82, 104, 101, 83, 52, 103, 86, 71, 104, 108, 73, 69, 70, 49, 100, 71, 104, 76, 90, 88, 107, 103, 97, 88, 77, 103, 86, 109, 86, 121, 101, 86, 90, 108, 99, 110, 108, 85, 98, 50, 53, 110, 86, 71, 57, 117, 90, 48, 100, 49, 99, 109, 107, 104]

def main():
    # 1. Hex representation
    hex_str = ''.join(f'{x:02x}' for x in DATA)
    print(f"HEX: {hex_str}")

    # 2. String representation
    try:
        raw_str = ''.join(chr(x) for x in DATA)
        print(f"RAW: {raw_str}")
        
        # 3. Base64 decoding (if the raw string looks like Base64)
        try:
            decoded = base64.b64decode(raw_str).decode('utf-8')
            print(f"B64 DECODED: {decoded}")
        except Exception:
            pass
            
    except ValueError:
        print("RAW: (Contains non-ASCII values)")

if __name__ == "__main__":
    main()

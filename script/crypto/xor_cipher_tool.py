#!/usr/bin/env python3
"""
General Purpose XOR Utility
Supports XORing with a key, a repeated key, or finding a key given known plaintext/ciphertext.
"""

import sys
import argparse
from itertools import cycle

def xor_data(data, key):
    return bytes([d ^ k for d, k in zip(data, cycle(key))])

def find_key(ciphertext, plaintext):
    return bytes([c ^ p for c, p in zip(ciphertext, plaintext)])

def main():
    parser = argparse.ArgumentParser(description="XOR Utility")
    parser.add_argument("-f", "--file", help="Input file to XOR")
    parser.add_argument("-k", "--key", help="Key (string or hex with 0x)")
    parser.add_argument("-o", "--output", help="Output file")
    parser.add_argument("--find-key", nargs=2, metavar=('CIPHER', 'PLAIN'), help="Hex strings of ciphertext and known plaintext to find key")
    
    args = parser.parse_args()

    if args.find_key:
        cipher = bytes.fromhex(args.find_key[0].replace(" ", ""))
        plain = bytes.fromhex(args.find_key[1].replace(" ", ""))
        key = find_key(cipher, plain)
        print(f"[+] Found Key (Hex): {key.hex().upper()}")
        print(f"[+] Found Key (Raw): {key}")
        return

    if not args.file or not args.key:
        parser.print_help()
        return

    # Parse key
    if args.key.startswith("0x"):
        key = bytes.fromhex(args.key[2:])
    else:
        key = args.key.encode()

    try:
        with open(args.file, "rb") as f:
            data = f.read()
        
        result = xor_data(data, key)
        
        if args.output:
            with open(args.output, "wb") as f:
                f.write(result)
            print(f"[+] Result saved to {args.output}")
        else:
            print(f"[+] Result (Hex): {result.hex()}")
            try:
                print(f"[+] Result (Raw): {result.decode()}")
            except UnicodeDecodeError:
                pass
    except Exception as e:
        print(f"[!] Error: {e}")

if __name__ == "__main__":
    main()

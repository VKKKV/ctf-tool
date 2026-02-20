#!/usr/bin/env python3
"""
Base64 Tool
Encodes or decodes data from stdin.
"""

import sys
import base64
import argparse

def main():
    parser = argparse.ArgumentParser(description="Base64 Encode/Decode Tool")
    parser.add_argument("-d", "--decode", action="store_true", help="Decode instead of encode")
    args = parser.parse_args()

    try:
        for line in sys.stdin:
            data = line.strip()
            if not data:
                continue
            
            try:
                if args.decode:
                    result = base64.b64decode(data).decode()
                else:
                    result = base64.b64encode(data.encode()).decode()
                print(result)
            except Exception as e:
                print(f"[!] Error: {e}", file=sys.stderr)
    except KeyboardInterrupt:
        pass

if __name__ == "__main__":
    main()

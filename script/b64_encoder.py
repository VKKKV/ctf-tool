#!/usr/bin/env python3
"""
Simple Base64 Encoder
Reads lines from standard input and prints their Base64 encoded representation.
"""

import sys
import base64

def main():
    try:
        for line in sys.stdin:
            # Strip trailing whitespace/newlines and encode
            data = line.strip()
            if not data:
                continue
            
            encoded = base64.b64encode(data.encode()).decode()
            print(encoded)
    except KeyboardInterrupt:
        pass

if __name__ == "__main__":
    main()

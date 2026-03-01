#!/usr/bin/env python3
"""
String Generator / Brute-force Payload Generator
Generates strings with a fixed prefix, middle part from a charset, and fixed suffix.
"""

import itertools
import sys

# --- Configuration ---
CHARSET = "0123456789_ABCDEFGHIJKLMNOPQRSTUVWXYZ"
PREFIX = "H4"
SUFFIX = "N_TH3_MIDD33_4TT4CK"
LENGTH = 5  # Length of the variable middle part


def generate_payloads(length):
    """Generates all combinations of CHARSET of a given length."""
    # Using itertools.product is much more efficient and cleaner than nested loops
    for combo in itertools.product(CHARSET, repeat=length):
        middle = "".join(combo)
        yield f"{PREFIX}{middle}{SUFFIX}"


def main(length=LENGTH):
    print(f"[*] Generating payloads of length {length}...")
    print(f"[*] Total combinations: {len(CHARSET) ** length:,}")

    try:
        # Warning: This can produce massive output
        for payload in generate_payloads(length):
            print(payload)
    except KeyboardInterrupt:
        print("\n[!] Interrupted by user.")


if __name__ == "__main__":
    # Note: 36^5 is over 60 million. Use with caution!
    if len(sys.argv) > 1:
        main(int(sys.argv[1]))
    else:
        print("[!] Defaulting to length 1. Pass an argument to change length.")
        main(1)

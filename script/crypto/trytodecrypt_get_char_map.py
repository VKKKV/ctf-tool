#!/usr/bin/env python3
"""Build character mapping from trytodecrypt.com encrypt API.

Usage: trytodecrypt_get_char_map.py <text_id> <api_key>

Encrypts each character in the charset via the API, maps
full response -> character. Parallel requests for speed.
Outputs a sorted Python dict literal.
"""
import sys
import urllib.parse
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed

C = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ-_.,;:?! "
URL = "http://api.trytodecrypt.com/encrypt?key={key}&id={id}&text={text}"


def encrypt(ch, text_id, api_key):
    url = URL.format(key=api_key, id=text_id, text=urllib.parse.quote(ch))
    try:
        with urllib.request.urlopen(url, timeout=10) as resp:
            return resp.read().decode().strip()
    except Exception as e:
        return None


if __name__ == "__main__":
    text_id = sys.argv[1]
    api_key = sys.argv[2]

    mapping = {}
    total = len(C)
    with ThreadPoolExecutor(max_workers=12) as pool:
        fut_map = {pool.submit(encrypt, ch, text_id, api_key): ch for ch in C}
        for i, fut in enumerate(as_completed(fut_map), 1):
            ch = fut_map[fut]
            enc = fut.result()
            if enc:
                mapping[enc] = ch
            print(f"\r  [{i}/{total}] {repr(ch)} -> {enc or 'FAIL'}" + " " * 10,
                  end="", file=sys.stderr, flush=True)
    print(file=sys.stderr)

    if mapping:
        print({k: mapping[k] for k in sorted(mapping.keys())})
    else:
        print("{}")
        sys.exit(1)

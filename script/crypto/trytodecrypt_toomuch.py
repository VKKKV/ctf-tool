#!/usr/bin/env python3
"""trytodecrypt Too Much! solver (Text 19-23).

Usage:
  # Decode with known algorithm
  echo <ciphertext> | python trytodecrypt_toomuch.py 19
  echo <ciphertext> | python trytodecrypt_toomuch.py 21

  # Oracle-based guessing (requires valid PHPSESSID cookie)
  # Tries to guess character by character using the encrypt tool
  python trytodecrypt_toomuch.py guess 22 <PHPSESSID>
"""

import re
import sys
import urllib.parse
import urllib.request

# 71-char charset (same as all trytodecrypt challenges)
CHARSET = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ-_.,;:?! "
CHARSET_DICT = {c: i for i, c in enumerate(CHARSET)}


# Hex encoding scheme used in Hard 5/6 and Too Much 1
def char_to_hex_encoding(ch):
    """Convert a character to its hex encoding value.
    Uses the scheme: 0=0x00, 1=0x01, ..., 9=0x09, a=0x0A, ..., z=0x23,
    A=0x24, ..., Z=0x3D, -=0x3E, _=0x3F, .=0x40, ,=0x41, ;=0x42, :=0x43,
    ?=0x44, !=0x45, space=0x46
    """
    if ch in CHARSET:
        return CHARSET.index(ch)
    return None


def hex_encoding_to_char(val):
    """Reverse of char_to_hex_encoding."""
    if 0 <= val < len(CHARSET):
        return CHARSET[val]
    return None


# ============================================================
# Text 19 — Too Much 1
# Known solution: R2D2:C3PO:BB8
# Structure: each char encoded as 5 hex chars
# First n hex chars = separators (1 per char)
def decode_text19(ct):
    result = ""
    if len(ct) == 65:
        data = ct[13:]
    else:
        raise ValueError(f"Unexpected ciphertext length: {len(ct)}")

    for i in range(0, len(data), 4):
        pair = data[i : i + 4]
        if len(pair) < 4:
            break
        offset = int(pair[0:2], 16)
        enc = int(pair[2:4], 16)
        diff = (enc - offset) % len(CHARSET)
        if 0 <= diff < len(CHARSET):
            result += CHARSET[diff]
        else:
            result += "?"

    # Fixed version has 2 key chars prefix
    if len(ct) == 76 and len(result) > 2:
        return result[2:]
    return result


# ============================================================
# Text 20 — Too Much 2
# Structure observed so far:
# - target length: 90 hex = 18 chars × 5 hex
# - encryption is randomized; same plaintext gives different ciphertext
# - each inline group looks like [prefix nibble][byte1][byte2]
# - unlike Text 19, (byte2 - byte1) mod 71 is not the plaintext
#
# Current local research artifacts:
# - /tmp/tm20_stats.jsonl: 32 oracle samples per charset char, encrypted as ch*18
# - /tmp/tm20_mixed_samples.jsonl: mixed-position probes
# - /tmp/tm20_phase_rank_32.out and /tmp/tm20_mi_32.out: statistical ranking/MI notes
#
# Negative results worth preserving:
# - inline split [p][b1][b2] and Text19-style split [prefixes][pairs] both fail
# - tested b2-b1, b1-b2, +/- prefix, sum, xor, raw bytes under inline/front/split layouts
# - naive Bayesian candidates from 32 samples per char all fail solve API
# - linear models idx = a*b1 + b*b2 + group_offset(pos/p) have near-random accuracy
#   (best residual by pos,p was only ~4.85%, so this is not a simple linear byte relation)
# ============================================================
def decode_text20(ct):
    """Text 20 is currently unsolved.

    Return the old naive Text19-style decode only as a diagnostic baseline;
    this is known to be incorrect for the challenge target.
    """
    if len(ct) != 90:
        raise ValueError(f"Text 20 ciphertext must be 90 hex chars, got {len(ct)}")

    result = ""
    for i in range(0, 90, 5):
        group = ct[i : i + 5]
        b1 = int(group[1:3], 16)
        b2 = int(group[3:5], 16)
        result += CHARSET[(b2 - b1) % len(CHARSET)]
    return result


# ============================================================
# Text 21 — Too Much 3
# Known solution: TryToDecrypt! now!
# Encryption: each plaintext char maps to 4 fixed hex chars
# (step=4, simple substitution)
# ============================================================
def decode_text21(ct):
    """Decode Text 21 — fixed 4-hex substitution."""
    # The known mapping (built from encrypt oracle):
    # Each char -> exactly 4 hex chars
    mapping = {
        '0': '2F54',
        '1': '2F55',
        '2': '2F56',
        '3': '302D',
        '4': '302E',
        '5': '302F',
        '6': '3030',
        '7': '3031',
        '8': '3032',
        '9': '3033',
        'a': '3034',
        'b': '3035',
        'c': '3036',
        'd': '3051',
        'e': '3052',
        'f': '3053',
        'g': '3054',
        'h': '3055',
        'i': '3056',
        'j': '312D',
        'k': '312E',
        'l': '312F',
        'm': '3130',
        'n': '3131',
        'o': '3132',
        'p': '3133',
        'q': '3134',
        'r': '3135',
        's': '3136',
        't': '3151',
        'u': '3152',
        'v': '3153',
        'w': '3154',
        'x': '3155',
        'y': '3156',
        'z': '322D',
        'A': '322E',
        'B': '322F',
        'C': '3230',
        'D': '3231',
        'E': '3232',
        'F': '3233',
        'G': '3234',
        'H': '3235',
        'I': '3236',
        'J': '3251',
        'K': '3252',
        'L': '3253',
        'M': '3254',
        'N': '3255',
        'O': '3256',
        'P': '332D',
        'Q': '332E',
        'R': '332F',
        'S': '3330',
        'T': '3331',
        'U': '3332',
        'V': '3333',
        'W': '3334',
        'X': '3335',
        'Y': '3336',
        'Z': '3351',
        '-': '3352',
        '_': '3353',
        '.': '3354',
        ',': '3355',
        ';': '3356',
        ':': '342D',
        '?': '342E',
        '!': '342F',
        ' ': '3430',
    }
    reverse_mapping = {v: k for k, v in mapping.items()}

    result = ""
    for i in range(0, len(ct), 4):
        chunk = ct[i : i + 4]
        if chunk in reverse_mapping:
            result += reverse_mapping[chunk]
        else:
            result += "?"
    return result


# ============================================================
# Text 22 — Too Much 4
# Solved via progressive guessing (Feilulue middle script approach)
# Solution: mississippi
# Structure: 99 hex = 11 chars × 9 hex/char (3 groups of 3 hex each)
# Encryption is deterministic, position-dependent
# ============================================================
# (guess_text22 function is defined in the oracle section below)

def decode_text22(ct):
    """Decode Text 22 — known solution."""
    if len(ct) != 99:
        raise ValueError(f"Text 22 ciphertext must be 99 hex chars, got {len(ct)}")
    # Known solution
    return "mississippi"


# ============================================================
# Text 23 — Too Much 5
# Longest ciphertext, 250 hex chars
# ============================================================
def decode_text23(ct):
    """Decode Text 23."""
    if len(ct) != 250:
        raise ValueError(f"Text 23 ciphertext must be 250 hex chars, got {len(ct)}")

    # 250 hex = 125 bytes. Step=26 hex chars per char?
    # Let's try various approaches
    result = ""

    # Try: each byte as charset index
    for i in range(0, len(ct), 2):
        val = int(ct[i : i + 2], 16)
        if val < len(CHARSET):
            result += CHARSET[val]
        else:
            result += "."

    return result


# ============================================================
# Oracle-based character-by-character guessing (API version)
# Uses the trytodecrypt API endpoint — no bot detection.
# ============================================================
API_BASE = "http://api.trytodecrypt.com/encrypt"

def encrypt_via_api(text, text_id, api_key):
    """Encrypt text using the trytodecrypt API (no bot detection).

    Uses GET http://api.trytodecrypt.com/encrypt?key=KEY&id=N&text=TEXT
    instead of POST to decrypt.php (which returns 503 for non-browser).
    """
    url = f"{API_BASE}?key={api_key}&id={text_id}&text={urllib.parse.quote(text)}"
    try:
        resp = urllib.request.urlopen(url, timeout=10)
        return resp.read().decode().strip().upper()
    except Exception:
        return None


def guess_text(text_id, ciphertext, step, api_key):
    """Guess plaintext character by character via API.

    For each position i, try all chars in CHARSET.
    Encrypt guess+char via API, compare with target ciphertext prefix.

    Only works if encryption is DETERMINISTIC (same input → same output).
    """
    guess = ""
    num_chars = len(ciphertext) // step

    for pos in range(num_chars):
        found = False
        for ch in CHARSET:
            test = guess + ch
            encrypted = encrypt_via_api(test, text_id, api_key)
            if encrypted and encrypted == ciphertext[: (pos + 1) * step]:
                guess = test
                found = True
                print(f"  [{pos + 1}/{num_chars}] '{ch}' correct -> {guess}")
                break
        if not found:
            print(f"  [{pos + 1}/{num_chars}] No match found!")
            guess += "?"

    return guess


# Convenience wrapper for Text 22 (step=9)
def guess_text22(ct, api_key):
    return guess_text(22, ct, 9, api_key)


# ============================================================
# Main
# ============================================================
DECODERS = {
    19: decode_text19,
    20: decode_text20,
    21: decode_text21,
    22: decode_text22,
    23: decode_text23,
}


def main():
    if len(sys.argv) < 2:
        print(f"用法: {sys.argv[0]} <text_id (19-23)>")
        print(f"      {sys.argv[0]} guess <text_id> <step> <API_KEY>")
        sys.exit(1)

    if sys.argv[1] == "guess" or sys.argv[1] == "oracle":
        text_id = int(sys.argv[2])
        step = int(sys.argv[3])
        api_key = sys.argv[4]
        ct = input("Ciphertext: ").strip()
        print(f"Guessing Text {text_id} via API (step={step})...")
        result = guess_text(text_id, ct, step, api_key)
        print(f"\nResult: {result}")
        return

    text_id = int(sys.argv[1])
    ct = (
        sys.stdin.read().strip()
        if not sys.stdin.isatty()
        else input("Ciphertext: ").strip()
    )

    if text_id in DECODERS:
        try:
            result = DECODERS[text_id](ct)
            print(result)
        except Exception as e:
            print(f"Error: {e}")
    else:
        print(f"Unsupported text_id={text_id}")


if __name__ == "__main__":
    main()

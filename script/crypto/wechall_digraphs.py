#!/usr/bin/env python3
"""
WeChall Digraphs solver — digraph substitution cipher.

Usage:
    uv run wechall_digraphs.py --cookie 'WC=...'
    uv run wechall_digraphs.py --cookie 'WC=...' --submit   # auto-submit

Approach:
    1. Identify punctuation digraphs by word-end position
    2. Use word 0 "congratulations!" as anchor for letter mapping
    3. Cross-validate with short words (as, you, this, was, not, too...)
    4. Decode password from last word

This is a homophonic cipher — multiple digraphs can map to the same letter.
Word-structure analysis is more reliable than pure frequency analysis.
"""

import re
import sys
import argparse
import subprocess

CHALLENGE_URL = "https://www.wechall.net/en/challenge/training/crypto/digraph/index.php"

# Known plaintext word list (22 words, fixed structure)
KNOWN_PT = [
    "congratulations!", "you", "decrypted", "this", "message", "successfully!",
    "was", "not", "too", "difficult", "either.", "was", "it?", "well.",
    "good", "job!", "enter", "this", "keyword", "as", "solution:", None  # password
]


def fetch_page(cookie: str) -> str:
    r = subprocess.run(
        ["curl", "-sL", "--max-time", "15",
         "-b", cookie,
         "-H", "User-Agent: Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
               "(KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
         CHALLENGE_URL],
        capture_output=True, text=True, timeout=20
    )
    return r.stdout


def parse_page(html: str) -> tuple[str | None, str | None]:
    """Returns (cipher, csrf) or (None, None) if already solved / not found."""
    if "wc_chall_solved_1" in html:
        return None, None
    m = re.search(r">([a-z ]{40,})<", html)
    if not m:
        return None, None
    cipher = m.group(1).strip()
    csrf_m = re.search(r'gwf3_csrf.*?value="([^"]+)', html)
    csrf = csrf_m.group(1) if csrf_m else None
    return cipher, csrf


def build_mapping(words: list[str]) -> dict[str, str]:
    """Build digraph → character mapping from known plaintext structure."""
    mapping = {}

    # Word 0 "congratulations!" — primary anchor
    w0 = [words[0][i:i+2] for i in range(0, len(words[0])-1, 2)]
    for ch, dg in zip("congratulations!", w0):
        if dg not in mapping:
            mapping[dg] = ch

    # Punctuation by word-end position
    mapping[words[0][-2:]] = '!'   # congratulations! & successfully!
    mapping[words[13][-2:]] = '.'  # well. & either.
    mapping[words[12][-2:]] = '?'  # it?
    mapping[words[20][-2:]] = ':'  # solution:

    # Word-by-word alignment for remaining letters
    alignments = [
        ("solution:", 20), ("as", 19), ("you", 1), ("this", 3), ("was", 6),
        ("was", 11), ("not", 7), ("too", 8), ("message", 4),
        ("successfully!", 5), ("decrypted", 2), ("difficult", 9),
        ("either.", 10), ("well.", 13), ("good", 14), ("job!", 15),
        ("enter", 16), ("this", 17), ("keyword", 18), ("it?", 12),
    ]
    for pt_word, wi in alignments:
        dgs = [words[wi][i:i+2] for i in range(0, len(words[wi])-1, 2)]
        for ch, dg in zip(pt_word, dgs):
            if dg not in mapping:
                mapping[dg] = ch

    return mapping


def decode_words(mapping: dict[str, str], words: list[str]) -> list[str]:
    result = []
    for word in words:
        dgs = [word[i:i+2] for i in range(0, len(word)-1, 2)]
        result.append("".join(mapping.get(d, "?") for d in dgs))
    return result


def extract_password(mapping: dict[str, str], words: list[str]) -> str:
    """Decode last word and strip trailing punctuation."""
    w21 = [words[21][i:i+2] for i in range(0, len(words[21])-1, 2)]
    raw = "".join(mapping.get(d, "?") for d in w21)
    return raw.rstrip("!")


def submit(cookie: str, csrf: str, password: str) -> str:
    r = subprocess.run(
        ["curl", "-sL", "--max-time", "15",
         "-b", cookie,
         "-H", "User-Agent: Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
               "(KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
         "--data-urlencode", f"answer={password}",
         "--data-urlencode", "solve=Submit",
         "--data-urlencode", f"gwf3_csrf={csrf}",
         CHALLENGE_URL],
        capture_output=True, text=True, timeout=20
    )
    if "correct" in r.stdout.lower():
        return "correct"
    if "too much" in r.stdout.lower():
        return "rate_limited"
    if "token is invalid" in r.stdout.lower():
        return "csrf_expired"
    return "unknown"


def main():
    parser = argparse.ArgumentParser(description="WeChall Digraphs solver")
    parser.add_argument("--cookie", required=True, help="WC cookie value")
    parser.add_argument("--submit", action="store_true", help="Auto-submit answer")
    args = parser.parse_args()

    html = fetch_page(args.cookie)
    cipher, csrf = parse_page(html)

    if cipher is None:
        print("Already solved or page not found.")
        sys.exit(0)

    words = cipher.split(" ")
    print(f"Cipher: {len(words)} words, {len(cipher)} chars")

    mapping = build_mapping(words)
    decoded = decode_words(mapping, words)
    password = extract_password(mapping, words)

    print(f"Decoded: {' '.join(decoded)}")
    print(f"Password: {password}")

    if "?" in password:
        print(f"WARNING: unknown digraphs in password", file=sys.stderr)

    if args.submit:
        if csrf is None:
            print("ERROR: no CSRF token found", file=sys.stderr)
            sys.exit(1)
        result = submit(args.cookie, csrf, password)
        print(f"Submit: {result}")
    else:
        print(f"\nSubmit manually or rerun with --submit")


if __name__ == "__main__":
    main()

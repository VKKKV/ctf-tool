#!/usr/bin/env python3
"""
Comprehensive solver for trytodecrypt.com challenges.
Uses the website encrypt function to deduce plaintexts.
"""
import requests
import re
import string
import sys

CHARSET = string.digits + string.ascii_lowercase + string.ascii_uppercase + '-_.,;:?! '

def encrypt(id_num, text):
    """Use the website's encrypt form to encrypt text."""
    url = f"https://www.trytodecrypt.com/decrypt.php?id={id_num}"
    data = {"text": text, "encrypt": "Encrypt"}
    try:
        r = requests.post(url, data=data, timeout=10)
        match = re.search(r'this text encrypted:</div>\s*<div class="panel-body" style="word-wrap: break-word;">([^<]+)', r.text)
        if match:
            return match.group(1)
    except:
        pass
    return None

def analyze_pattern(id_num):
    """Analyze the encryption pattern for a given challenge."""
    print(f"=== Analyzing Challenge ID {id_num} ===")
    
    # Test various strings
    tests = [
        "a", "b", "0", "1", " ", ".",
        "aa", "ab", "abc",
        "aaaa", "abcdef",
        "aaaaaaaaaa",
    ]
    
    for t in tests:
        enc = encrypt(id_num, t)
        if enc:
            pairs = [enc[i:i+2] for i in range(0, len(enc), 2)]
            print(f"  '{t}' ({len(t)} chars) -> '{enc}' ({len(pairs)} pairs) {pairs}")

def solve_middle_positional(id_num, ciphertext, use_api=False):
    """
    Solve Middle challenges with position-dependent encoding.
    The encoding of a character depends on its position in the string.
    We encrypt test strings to figure out the mapping for each position.
    """
    print(f"\n=== Solving Middle ID {id_num} ===")
    print(f"Ciphertext: {ciphertext}")
    
    ct_pairs = [ciphertext[i:i+2] for i in range(0, len(ciphertext), 2)]
    n_chars = len(ct_pairs)
    print(f"Number of hex pairs: {n_chars}")
    
    # Method: Try encrypting a single char to see how it encodes.
    # For positional ciphers, encrypt('a') might give a different result 
    # than encrypt('aa') as the position of 'a' in the second case is different.
    # We need to encrypt strings of the right length.
    
    # Let's first determine: does each char encrypt to 2 hex digits?
    # Test with 'a'*n for various n
    for n in range(1, 6):
        enc = encrypt(id_num, 'a' * n)
        if enc:
            print(f"  {'a'*n} (n={n}) -> {enc} ({len(enc)//2} pairs)")
            if len(enc)//2 == n + 1:  # key prefix?
                print(f"    Pattern: key={enc[:2]}, chars: {[enc[i:i+2] for i in range(2, len(enc), 2)]}")
    
    # Try to figure out the plaintext by position-by-position guessing
    # For each position, try all possible characters
    result = ""
    
    for pos in range(n_chars):
        found = False
        for ch in CHARSET:
            # Build a test string of length pos+1 ending with the candidate char
            test = result + ch
            enc = encrypt(id_num, test)
            if enc:
                enc_pairs = [enc[i:i+2] for i in range(0, len(enc), 2)]
                # For position-dependent encoding without key prefix,
                # the encoding of each position should match
                if len(enc_pairs) == len(test):
                    if enc_pairs[pos] == ct_pairs[pos]:
                        result += ch
                        print(f"  Position {pos}: found '{ch}' -> {result}")
                        found = True
                        break
        if not found:
            print(f"  Position {pos}: NOT FOUND")
            result += "?"
    
    print(f"\n  Result: '{result}'")
    return result

def solve_hard_simple(id_num, ciphertext, hex_char_map, rev_hex_map):
    """
    Solve Hard challenges with key+char_value encoding (like ID 13).
    """
    print(f"\n=== Solving Hard ID {id_num} with simple key+char encoding ===")
    print(f"Ciphertext: {ciphertext}")
    
    ct_pairs = [ciphertext[i:i+2] for i in range(0, len(ciphertext), 2)]
    print(f"Total pairs: {len(ct_pairs)}")
    
    # The first pair might be the key
    key = int(ct_pairs[0], 16)
    print(f"Assuming key = 0x{key:02X} ({key})")
    
    result = ""
    for p in ct_pairs[1:]:
        char_val = (int(p, 16) - key) & 0xFF
        ch = rev_hex_map.get(char_val, f"[{hex(char_val)}]")
        result += ch
    
    print(f"Decoded: '{result}'")
    return result

# Define hex encoding scheme
hex_char_map = {}
rev_hex_map = {}

for i, c in enumerate(string.digits):
    hex_char_map[c] = i
    rev_hex_map[i] = c
for i, c in enumerate(string.ascii_lowercase):
    hex_char_map[c] = 0x0A + i
    rev_hex_map[0x0A + i] = c
for i, c in enumerate(string.ascii_uppercase):
    hex_char_map[c] = 0x24 + i
    rev_hex_map[0x24 + i] = c

# Special chars from Paul Frisby's notes
specials = {
    ' ': 0x46, '.': 0x40, ',': 0x41, ';': 0x42, 
    ':': 0x43, '?': 0x44, '!': 0x45, '-': 0x47, '_': 0x48
}
for ch, val in specials.items():
    hex_char_map[ch] = val
    rev_hex_map[val] = ch

# Problem ciphertexts
challenges = {
    # Middle
    10: "261129152E152B",
    11: "3785824AD56B2531A7150DF44C21434A61E63F040A42F2012BC2F43F0AD535D24D46013213866D7E0",
    12: "00D02703603C0450461340870A50B50EA10A0BD133",
    # Hard
    13: "59656A6B6F9F656A67746767",
    14: "6F5657A6606B7D9C7480649D7A6B757D9C70816B6CB4",
    # Too Much!
    20: "8221E4F2173368D6B6B6E5050935D986A8C4CA764CF8A8C4B734E99807140B19DB691998095CC4E3D6C60D6E91",
    21: "333131353156333131323231305230363135315631333151342F3430313131323154342F",
    22: "00100401400A0120A101C0310F503706004E05B0870A00880D80ED0BE1262890FD16816A1453453721963ED1D11F04624D9",
    23: "E3F59F001361B62958E551B9702F2C6B25F9E3FC350062295A1A20182041493C447BA0767A393A1F278DB14268565F51575C65212A8386494B383F7375676845472F30494C737A406890988B8D50577A835960476B6F73686E6367668B787A494C33357EA4555E191C18216A6F353A173E2026474A8A8C3F481416759D",
}

if __name__ == "__main__":
    # First, let's analyze the pattern for each challenge
    for id_num in [10, 11, 12, 13, 14]:
        print("\n" + "="*60)
        analyze_pattern(id_num)
    
    # Then try to decode using the simple key approach for Hard
    print("\n\n=== Hard Challenge Decoding ===")
    for id_num in [13, 14]:
        result = solve_hard_simple(id_num, challenges[id_num], hex_char_map, rev_hex_map)
    
    # For Middle, try positional solving
    print("\n\n=== Middle Challenge Analysis ===")
    for id_num in [10, 11, 12]:
        ct = challenges[id_num]
        # Check if this looks like it has a key prefix
        print(f"\nID {id_num}: {ct} (len={len(ct)}, pairs={len(ct)//2})")
        # Test what encrypting a single char returns
        for t in ['a', '0', 'ab', 'abc']:
            enc = encrypt(id_num, t)
            if enc:
                print(f"  '{t}' -> {enc}")

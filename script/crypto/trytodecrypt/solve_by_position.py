#!/usr/bin/env python3
"""
Solver for trytodecrypt.com challenges using positional analysis.
"""
import requests
import re
import string

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
    except Exception as e:
        print(f"  Error: {e}")
    return None

def solve_by_positional_guess(id_num, ciphertext, chars_per_char=2):
    """
    Solve by guessing each character position by position.
    We encrypt progressively longer strings and compare with ciphertext.
    This works when encoding is position-dependent but deterministic.
    """
    print(f"\n=== Solving ID {id_num} (positional guess, {chars_per_char} hex/char) ===")
    
    # The ciphertext might have some initial prefix that's not part of the plaintext
    ct = ciphertext
    total_hex = len(ct)
    
    if chars_per_char == 2:
        n_chars = total_hex // 2
    elif chars_per_char == 3:
        n_chars = total_hex // 3
    else:
        n_chars = total_hex // chars_per_char
    
    print(f"Ciphertext: {ct} ({total_hex} hex chars, {n_chars} expected plaintext chars)")
    
    result = ""
    
    for pos in range(n_chars):
        found = False
        for ch in CHARSET:
            test = result + ch
            enc = encrypt(id_num, test)
            if enc is None:
                continue
            
            # Compare the relevant part
            # For positional encoding, the encryption of test should match 
            # the first (pos+1) * chars_per_char hex chars of the ciphertext
            target_prefix = ct[:(pos+1) * chars_per_char]
            
            if enc == target_prefix:
                result += ch
                print(f"  Pos {pos}: '{ch}' -> '{result}'")
                found = True
                break
        
        if not found:
            print(f"  Pos {pos}: NOT FOUND (trying all chars...)")
            # Debug: try a few and see what encrypt returns
            for ch in CHARSET[:5]:
                test = result + ch
                enc = encrypt(id_num, test)
                print(f"    Trying '{ch}': encrypts to '{enc}'")
            result += "?"
    
    print(f"\n>>> SOLUTION: '{result}'")
    return result

# Ciphertexts
challenges = {
    10: "261129152E152B",
    11: "3785824AD56B2531A7150DF44C21434A61E63F040A42F2012BC2F43F0AD535D24D46013213866D7E0",
    12: "00D02703603C0450461340870A50B50EA10A0BD133",
    13: "59656A6B6F9F656A67746767",
    14: "6F5657A6606B7D9C7480649D7A6B757D9C70816B6CB4",
    20: "8221E4F2173368D6B6B6E5050935D986A8C4CA764CF8A8C4B734E99807140B19DB691998095CC4E3D6C60D6E91",
    21: "333131353156333131323231305230363135315631333151342F3430313131323154342F",
    22: "00100401400A0120A101C0310F503706004E05B0870A00880D80ED0BE1262890FD16816A1453453721963ED1D11F04624D9",
    23: "E3F59F001361B62958E551B9702F2C6B25F9E3FC350062295A1A20182041493C447BA0767A393A1F278DB14268565F51575C65212A8386494B383F7375676845472F30494C737A406890988B8D50577A835960476B6F73686E6367668B787A494C33357EA4555E191C18216A6F353A173E2026474A8A8C3F481416759D",
}

# First determine the pattern
print("=== Determining encryption patterns ===")
for id_num, ct in sorted(challenges.items()):
    print(f"\nID {id_num}: ct={ct[:30]}... (len={len(ct)})")
    # Test encrypting single chars
    for t in ['a', 'b', '0', '1', ' ']:
        enc = encrypt(id_num, t)
        if enc:
            print(f"  '{t}' ({len(t)} char) -> '{enc}' ({len(enc)} hex)")
    
    # Test encrypting 2 chars  
    for t in ['aa', 'ab']:
        enc = encrypt(id_num, t)
        if enc:
            print(f"  '{t}' ({len(t)} chars) -> '{enc}' ({len(enc)} hex)")

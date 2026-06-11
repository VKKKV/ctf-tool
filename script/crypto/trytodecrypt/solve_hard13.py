#!/usr/bin/env python3
"""
Solve Hard 1 (ID 13) from trytodecrypt.com
Ciphertext: 59656A6B6F9F656A67746767
"""
import requests
import re
import string

def encrypt(id_num, text):
    """Use the website's encrypt form to encrypt text."""
    url = f"https://www.trytodecrypt.com/decrypt.php?id={id_num}"
    data = {"text": text, "encrypt": "Encrypt"}
    r = requests.post(url, data=data, timeout=10)
    # Extract the encrypted result
    match = re.search(r'this text encrypted:</div>\s*<div class="panel-body" style="word-wrap: break-word;">([^<]+)', r.text)
    if match:
        return match.group(1)
    return None

def try_solution(id_num, solution):
    """Submit a solution to check if it's correct."""
    url = f"https://www.trytodecrypt.com/decrypt.php?id={id_num}"
    data = {"text": solution, "solutionButton": "this is the solution!"}
    r = requests.post(url, data=data, timeout=10)
    # Check for success message
    if "congratulation" in r.text.lower() or "correct" in r.text.lower() or "solved" in r.text.lower():
        return True, r.text
    return False, r.text

# Character set from the problem
charset = string.digits + string.ascii_lowercase + string.ascii_uppercase + '-_.,;:?! '

# Known hex encoding scheme (from Paul Frisby's notes)
hex_chars = {}
for i, c in enumerate(string.digits):
    hex_chars[c] = i
for i, c in enumerate(string.ascii_lowercase):
    hex_chars[c] = 0x0A + i
for i, c in enumerate(string.ascii_uppercase):
    hex_chars[c] = 0x24 + i
# Special chars
hex_chars[' '] = 0x46
hex_chars['.'] = 0x40
hex_chars[','] = 0x41
hex_chars[';'] = 0x42
hex_chars[':'] = 0x43
hex_chars['?'] = 0x44
hex_chars['!'] = 0x45
hex_chars['-'] = 0x47
hex_chars['_'] = 0x48

# Reverse mapping
rev_hex = {v: k for k, v in hex_chars.items()}

def decode_hard13(ciphertext):
    """Decode Text 13 using the formula: encoded = key + char_value."""
    pairs = [ciphertext[i:i+2] for i in range(0, len(ciphertext), 2)]
    key = int(pairs[0], 16)
    result = ""
    for p in pairs[1:]:
        val = int(p, 16) - key
        if val in rev_hex:
            result += rev_hex[val]
        else:
            result += f"[{hex(val)}]"
    return result

# The ciphertext
ct = "59656A6B6F9F656A67746767"
print(f"Ciphertext: {ct}")
plain = decode_hard13(ct)
print(f"Decoded: '{plain}'")

# Verify by encrypting the decoded text and checking if it matches the pattern
print(f"\nVerifying by encrypting the decoded text...")
enc = encrypt(13, plain)
print(f"Encrypted form: {enc}")

if enc:
    # The key changes each time, but the encoded chars relative to key should match
    enc_pairs = [enc[i:i+2] for i in range(0, len(enc), 2)]
    enc_key = int(enc_pairs[0], 16)
    print(f"Encryption key: {hex(enc_key)}")
    decoded_check = ""
    for p in enc_pairs[1:]:
        val = int(p, 16) - enc_key
        if val in rev_hex:
            decoded_check += rev_hex[val]
        else:
            decoded_check += f"[{hex(val)}]"
    print(f"Decoded from encrypted form: '{decoded_check}'")
    print(f"Match: {plain == decoded_check}")

# Try submitting the solution
print(f"\nTrying to submit solution...")
# Check if the website confirms it
url = f"https://www.trytodecrypt.com/decrypt.php?id=13"
data = {"text": plain, "solutionButton": "this is the solution!"}
r = requests.post(url, data=data, timeout=10)
if "Congratulation" in r.text or "correct" in r.text.lower():
    print("SUCCESS! Solution is correct!")
    print(f"Plaintext: {plain}")
elif "wrong" in r.text.lower() or "not correct" in r.text.lower():
    print("Solution was wrong.")
else:
    # Check what the page says
    if "solved" in r.text.lower():
        print("Solution might be correct (solved keyword found)")
    # Extract any alert/error messages
    alerts = re.findall(r'<div[^>]*class="[^"]*alert[^"]*"[^>]*>([^<]+)', r.text)
    if alerts:
        for a in alerts:
            print(f"Alert: {a.strip()}")
    print("Could not determine. Check manually.")
    # Print a snippet of the response
    snippet = r.text[3000:4000]
    print(f"Response snippet: {snippet[:200]}")

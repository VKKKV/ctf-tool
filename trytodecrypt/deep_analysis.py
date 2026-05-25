#!/usr/bin/env python3
"""
Extended analysis of unsolved TryToDecrypt challenges.
Focus on promising leads and Text 21 double-encoding.
"""
import string

CHARSET = string.digits + string.ascii_lowercase + string.ascii_uppercase + '-_.,;:?! '
HARD_MAP = {}
for i in range(10):
    HARD_MAP[i] = chr(ord('0') + i)
for i in range(26):
    HARD_MAP[0x0A + i] = chr(ord('a') + i)
for i in range(26):
    HARD_MAP[0x24 + i] = chr(ord('A') + i)
HARD_MAP[0x40] = '.'
HARD_MAP[0x46] = ' '

def hard_decode(val):
    return HARD_MAP.get(val, '?')

def charset_decode(val):
    if 0 <= val < len(CHARSET):
        return CHARSET[val]
    return '?'

# Text 13 - try various chunk schemes
print("=" * 60)
print("TEXT 13 - Detailed analysis")
print("=" * 60)
ct13 = "59656A6B6F9F656A67746767"
print(f"Ciphertext: {ct13}")

# Method A: 4-char chunks, offset+encoded
print("\nA) 4-char chunks (offset , encoded):")
for i in range(0, len(ct13), 4):
    chunk = ct13[i:i+4]
    off = int(chunk[0:2], 16)
    enc = int(chunk[2:4], 16)
    diff = enc - off
    print(f"   {chunk}: off=0x{off:02X}, enc=0x{enc:02X}, diff={diff} ({hex(diff)}) -> charset='{charset_decode(diff & 0xFF)}' hard='{hard_decode(diff & 0xFF)}'")

# Method B: Split into halves
print("\nB) Split halves (first half = keys, second = data):")
half = len(ct13)//2
first = ct13[:half]
second = ct13[half:]
print(f"   First half: {first}")
print(f"   Second half: {second}")
for i in range(0, half, 2):
    k = int(first[i:i+2], 16)
    d = int(second[i:i+2], 16)
    diff = d - k
    print(f"   k=0x{k:02X}, d=0x{d:02X}, d-k={diff} ({hex(diff & 0xFF)}) -> '{charset_decode(diff & 0xFF)}'")
    diff2 = k - d
    print(f"     k-d={diff2} ({hex(diff2 & 0xFF)}) -> '{charset_decode(diff2 & 0xFF)}'")

# Method C: Try each pair as charset index
print("\nC) Each hex pair as charset index:")
pairs = [ct13[i:i+2] for i in range(0, len(ct13), 2)]
for i, p in enumerate(pairs):
    val = int(p, 16)
    print(f"   {p}=0x{val:02X}={val} -> '{charset_decode(val)}'")
print(f"   Full: {''.join(charset_decode(int(p,16)) for p in pairs)}")

# Method D: What if it's 6-char chunks?
print("\nD) 6-char chunks (3 bytes per char?):")
for i in range(0, len(ct13), 6):
    chunk = ct13[i:i+6]
    if len(chunk) == 6:
        b1 = int(chunk[0:2], 16)
        b2 = int(chunk[2:4], 16)
        b3 = int(chunk[4:6], 16)
        print(f"   {chunk}: b1={b1:#04x}, b2={b2:#04x}, b3={b3:#04x}")

# Text 14 - similar analysis
print("\n\n" + "=" * 60)
print("TEXT 14 - Detailed analysis")
print("=" * 60)
ct14 = "6F5657A6606B7D9C7480649D7A6B757D9C70816B6CB4"
print(f"Ciphertext: {ct14}")

# Method A: 4-char chunks, offset+encoded
print("\nA) 4-char chunks:")
for i in range(0, len(ct14), 4):
    chunk = ct14[i:i+4]
    if len(chunk) == 4:
        off = int(chunk[0:2], 16)
        enc = int(chunk[2:4], 16)
        diff1 = (enc - off) & 0xFF
        diff2 = (off - enc) & 0xFF
        xor = off ^ enc
        print(f"   {chunk}: off=0x{off:02X}, enc=0x{enc:02X}, enc-off='{charset_decode(diff1)}', off-enc='{charset_decode(diff2)}', xor='{charset_decode(xor)}'")

# Method B: Split halves
print("\nB) Split halves:")
half = len(ct14)//2
first = ct14[:half]
second = ct14[half:]
print(f"   First half: {first}")
print(f"   Second half: {second}")
for i in range(0, half, 2):
    k = int(first[i:i+2], 16)
    d = int(second[i:i+2], 16)
    diff = (d - k) & 0xFF
    diff2 = (k - d) & 0xFF
    print(f"   k=0x{k:02X}, d=0x{d:02X}, d-k='{charset_decode(diff)}', k-d='{charset_decode(diff2)}'")

# Text 21 - double encoding analysis
print("\n\n" + "=" * 60)
print("TEXT 21 - Double encoding analysis")
print("=" * 60)
ct21 = "333131353156333131323231305230363135315631333151342F3430313131323154342F"
print(f"Original ciphertext: {ct21}")

# Decode hex
inner = bytes.fromhex(ct21).decode('ascii')
print(f"First decode (hex->ASCII): \"{inner}\"")

# The result is "31151V3112210R06151V131Q4/4011121T4/"
# Let me check: if I split this by specific delimiters...
# It has 'V' and 'R' and 'Q' and 'T' and '/'
# What if each group separated by these letters is meaningful?

# Try treating 'V', 'R', 'Q', 'T' as control characters
# And the numbers as values

# What if I group by pairs after the decode?
inner_pairs = [inner[i:i+2] for i in range(0, len(inner), 2)]
print(f"\nPairs from decoded string: {inner_pairs}")

# Check if pairs are valid hex
for p in inner_pairs:
    try:
        val = int(p, 16)
        ch = hard_decode(val)
        print(f"   '{p}' = 0x{val:02X} -> hard: '{ch}'")
    except ValueError:
        print(f"   '{p}' -> not valid hex")

# Also try as charset index
for p in inner_pairs:
    try:
        val = int(p, 16)
        ch = charset_decode(val)
        print(f"   '{p}' = {val} -> charset: '{ch}'")
    except ValueError:
        print(f"   '{p}' -> not valid hex")

# What if the inner decoded string is a URL or path?
# "31151V3112210R06151V131Q4/4011121T4/"
# Could be: /31151V3112210R06151V131Q4/4011121T4/
# Or maybe it's a path like /something/something

# What if I interpret 'V', 'R', 'Q', 'T' as mapping to something?
print(f"\nDecoded string with non-digit chars highlighted:")
for i, c in enumerate(inner):
    if c.isdigit():
        print(f"  pos {i}: '{c}' (digit)")
    else:
        print(f"  pos {i}: '{c}' (LETTER) ord={ord(c)}")

# Maybe the non-digit letters are punctuation replacements?
# V=space, R=space, Q=space, T=space?
# "31151 3112210 06151 131 4/4011121 4/"
# Hmm...

# Text 10 - trying different interpretations
print("\n\n" + "=" * 60)
print("TEXT 10 - Deeper analysis")
print("=" * 60)
ct10 = "261129152E152B"
pairs10 = [ct10[i:i+2] for i in range(0, len(ct10), 2)]
vals10 = [int(p, 16) for p in pairs10]

# Try as pairs (difference between consecutive)
print("Consecutive differences:")
for i in range(1, len(vals10)):
    diff = vals10[i] - vals10[i-1]
    print(f"  {vals10[i-1]:#x} -> {vals10[i]:#x}: diff={diff}")
    # Maybe the chars are encoded as these differences?
    ch = charset_decode(diff & 0xFF)
    print(f"    diff as charset: '{ch}'")

# Try each value as representing different things
print("\nEach value as...")
for i, v in enumerate(vals10):
    print(f"  pos {i}: val={v} ({hex(v)})")
    print(f"    charset: '{charset_decode(v)}'")
    print(f"    hard_encode: '{hard_decode(v)}'")
    # Try mod 71
    print(f"    mod 71: '{charset_decode(v % 71)}'")
    # Try subtracting i*10
    print(f"    -{i*10}: '{charset_decode((v - i*10) & 0xFF)}'")

# What if the answer is actually very simple?
# "26 11 29 15 2E 15 2B" 
# If these are already the plaintext in some encoding...
# Hard encode: C h F l K l H -> "ChFlKlH"
# This doesn't look right as English...

# Wait - what if the answer is ROT13 on the charset index?
print("\nTrying ROT-like on the charset:")
result = []
for v in vals10:
    # Reverse of: encrypted = (index + 13) % 71
    idx = (v - 13) % 71
    result.append(CHARSET[idx])
print(f"  ROT13-1: {''.join(result)}")

# Try various shifts on charset
for shift in range(1, 71):
    result = []
    ok = True
    for v in vals10:
        idx = (v - shift) % 71
        if 0 <= idx < len(CHARSET):
            result.append(CHARSET[idx])
        else:
            ok = False
            break
    if ok:
        r = ''.join(result)
        # Check if all printable and reasonable
        if all(c.isalnum() or c in '-_.,;:?! ' for c in r):
            print(f"  shift={shift}: {r}")

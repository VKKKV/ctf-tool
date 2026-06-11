#!/usr/bin/env python3
"""Analyze TryToDecrypt challenges and try different decryption approaches."""

import string
import binascii

# All ciphertexts
TEXTS = {
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

# The encoding scheme used in hard challenges 16-19
def hex_to_char(hex_val):
    """Convert hex encoded value to character using the scheme from hard challenges."""
    if hex_val <= 0x09:
        return chr(ord('0') + hex_val)
    elif 0x0A <= hex_val <= 0x23:
        return chr(ord('a') + hex_val - 0x0A)
    elif 0x24 <= hex_val <= 0x3D:
        return chr(ord('A') + hex_val - 0x24)
    elif hex_val == 0x40:
        return '.'
    elif hex_val == 0x46:
        return ' '
    else:
        # Try to find in special chars
        special = "-_.,;:?! "
        idx = hex_val - 0x3E
        if 0 <= idx < len(special):
            return special[idx]
        return '?'

# Character set (same as API)
CHARSET = string.digits + string.ascii_lowercase + string.ascii_uppercase + '-_.,;:?! '

def char_to_hex_encoding(c):
    """Convert a character to its hex value using the encoding scheme."""
    if c in string.digits:
        return ord(c) - ord('0')
    elif c in string.ascii_lowercase:
        return ord(c) - ord('a') + 0x0A
    elif c in string.ascii_uppercase:
        return ord(c) - ord('A') + 0x24
    elif c == '.':
        return 0x40
    elif c == ' ':
        return 0x46
    else:
        special = "-_.,;:?! "
        idx = special.find(c)
        if idx >= 0:
            return 0x3E + idx
    return None

# Approach 1: Try hex-decoding Text 21 (the hint suggests this)
print("=" * 60)
print("TEXT 21 ANALYSIS")
print("=" * 60)
raw21 = TEXTS[21]
print(f"Ciphertext: {raw21}")
try:
    decoded21 = bytes.fromhex(raw21).decode('ascii')
    print(f"Hex-decoded: {decoded21}")
except Exception as e:
    print(f"Error: {e}")

# What if the hex-decoded string itself is meaningful?
# Check if it could be a URL path
decoded21 = bytes.fromhex(raw21).decode('ascii')
print(f"Length: {len(decoded21)} chars")

# Try to interpret as pairs
print(f"\nPairs (2-char chunks):")
for i in range(0, len(decoded21), 2):
    chunk = decoded21[i:i+2]
    print(f"  {chunk}")

# Try to interpret each character
print(f"\nChars:")
for c in decoded21:
    print(f"  '{c}' (ord={ord(c)})")

# Approach 2: Analyze Text 10
print("\n" + "=" * 60)
print("TEXT 10 ANALYSIS")
print("=" * 60)
ct10 = TEXTS[10]
print(f"Ciphertext: {ct10}")
print(f"Length: {len(ct10)} hex chars = {len(ct10)//2} bytes")

# Split into hex pairs
pairs10 = [ct10[i:i+2] for i in range(0, len(ct10), 2)]
print(f"Hex pairs: {pairs10}")
print(f"As integers: {[int(p, 16) for p in pairs10]}")

# Try the simple encoding scheme
print(f"\nTrying direct hex-to-char (hard encoding scheme):")
for p in pairs10:
    h = int(p, 16)
    print(f"  {p} (0x{p}) -> '{hex_to_char(h)}'")

print(f"\nFull: {''.join(hex_to_char(int(p, 16)) for p in pairs10)}")

# Approach 3: Analyze Text 11  
print("\n" + "=" * 60)
print("TEXT 11 ANALYSIS")
print("=" * 60)
ct11 = TEXTS[11]
print(f"Ciphertext: {ct11}")
print(f"Length: {len(ct11)} hex chars = {len(ct11)//2} bytes")

# Split into hex pairs  
pairs11 = [ct11[i:i+2] for i in range(0, len(ct11), 2)]
print(f"First 10 hex pairs: {pairs11[:10]}")
print(f"As integers (first 10): {[int(p, 16) for p in pairs11[:10]]}")

# Check for patterns
print(f"\nChecking if Text 11 might use same algorithm as Text 5 (Easy 5):")
# Easy 5: encrypted = pos*3+12
# Let's try different encodings

# Approach 4: Analyze Text 12
print("\n" + "=" * 60)
print("TEXT 12 ANALYSIS")
print("=" * 60)
ct12 = TEXTS[12]
print(f"Ciphertext: {ct12}")
print(f"Length: {len(ct12)} hex chars = {len(ct12)//2} bytes")
pairs12 = [ct12[i:i+2] for i in range(0, len(ct12), 2)]
print(f"Hex pairs: {pairs12}")
print(f"As integers: {[int(p, 16) for p in pairs12]}")

# Check if pairs could be offset+encoded (4-char per char pattern like hard 16)
print(f"\nFour-char chunks (offset+encoded pattern):")
chunks4_12 = [ct12[i:i+4] for i in range(0, len(ct12), 4)]
for c in chunks4_12:
    if len(c) == 4:
        offset = int(c[0:2], 16)
        encoded = int(c[2:4], 16)
        decoded_val = (encoded - offset) & 0xFF
        print(f"  {c}: offset=0x{c[0:2]}({offset}), encoded=0x{c[2:4]}({encoded}), decoded=0x{decoded_val:02X} -> '{hex_to_char(decoded_val)}'")

# Approach 5: Analyze Text 13 (Hard)
print("\n" + "=" * 60)
print("TEXT 13 ANALYSIS")
print("=" * 60)
ct13 = TEXTS[13]
print(f"Ciphertext: {ct13}")
print(f"Length: {len(ct13)} hex chars = {len(ct13)//2} bytes")
pairs13 = [ct13[i:i+2] for i in range(0, len(ct13), 2)]
print(f"Hex pairs: {pairs13}")
print(f"As integers: {[int(p, 16) for p in pairs13]}")

# Try various split patterns
print(f"\nTrying 4-char chunks:")
chunks4_13 = [ct13[i:i+4] for i in range(0, len(ct13), 4)]
for c in chunks4_13:
    if len(c) == 4:
        offset = int(c[0:2], 16)
        encoded = int(c[2:4], 16)
        decoded_val = (encoded - offset) & 0xFF
        print(f"  {c}: offset=0x{c[0:2]}({offset}), encoded=0x{c[2:4]}({encoded}), decoded=0x{decoded_val:02X} -> '{hex_to_char(decoded_val)}'")
        # Try other operations
        decoded_val2 = (offset - encoded) & 0xFF
        decoded_val3 = offset ^ encoded
        print(f"    offset-encoded=0x{decoded_val2:02X} -> '{hex_to_char(decoded_val2)}', XOR=0x{decoded_val3:02X} -> '{hex_to_char(decoded_val3)}'")

# Also try 2-char simple encoding
print(f"\nDirect hex-to-char:")
for p in pairs13:
    h = int(p, 16)
    print(f"  {p} -> '{hex_to_char(h)}'")
print(f"Full: {''.join(hex_to_char(int(p, 16)) for p in pairs13)}")

# Approach 6: Analyze Text 14
print("\n" + "=" * 60)
print("TEXT 14 ANALYSIS")
print("=" * 60)
ct14 = TEXTS[14]
pairs14 = [ct14[i:i+2] for i in range(0, len(ct14), 2)]
print(f"Hex pairs: {pairs14}")
print(f"As integers: {[int(p, 16) for p in pairs14]}")

print(f"\n4-char chunks:")
chunks4_14 = [ct14[i:i+4] for i in range(0, len(ct14), 4)]
for c in chunks4_14:
    if len(c) == 4:
        offset = int(c[0:2], 16)
        encoded = int(c[2:4], 16)
        decoded_val = (encoded - offset) & 0xFF
        print(f"  {c}: offset-encoded={decoded_val:02X} -> '{hex_to_char(decoded_val)}'")
        decoded_val2 = (offset - encoded) & 0xFF
        print(f"    encoded-offset={decoded_val2:02X} -> '{hex_to_char(decoded_val2)}'")

# Approach 7: Analyze Text 20
print("\n" + "=" * 60)
print("TEXT 20 ANALYSIS")
print("=" * 60)
ct20 = TEXTS[20]
print(f"Length: {len(ct20)} hex chars")
pairs20 = [ct20[i:i+2] for i in range(0, len(ct20), 2)]
print(f"First 10 hex pairs as int: {[int(p, 16) for p in pairs20[:10]]}")

# Approach 8: Analyze Text 22
print("\n" + "=" * 60)
print("TEXT 22 ANALYSIS")
print("=" * 60)
ct22 = TEXTS[22]
print(f"Length: {len(ct22)} hex chars = {len(ct22)//2} bytes")
pairs22 = [ct22[i:i+2] for i in range(0, len(ct22), 2)]
print(f"First 15 hex pairs: {pairs22[:15]}")
print(f"As integers (first 15): {[int(p, 16) for p in pairs22[:15]]}")

# Approach 9: Analyze Text 23  
print("\n" + "=" * 60)
print("TEXT 23 ANALYSIS")
print("=" * 60)
ct23 = TEXTS[23]
print(f"Length: {len(ct23)} hex chars = {len(ct23)//2} bytes")
pairs23 = [ct23[i:i+2] for i in range(0, len(ct23), 2)]
print(f"First 20 hex pairs: {pairs23[:20]}")
print(f"As integers (first 20): {[int(p, 16) for p in pairs23[:20]]}")

# Look at byte value distribution
print(f"\nByte value analysis:")
for name, ct in [("Text 10", TEXTS[10]), ("Text 11", TEXTS[11]), ("Text 12", TEXTS[12]),
                 ("Text 13", TEXTS[13]), ("Text 14", TEXTS[14])]:
    pairs = [int(ct[i:i+2], 16) for i in range(0, len(ct), 2)]
    min_v = min(pairs)
    max_v = max(pairs)
    avg_v = sum(pairs) / len(pairs)
    print(f"  {name}: min=0x{min_v:02X}({min_v}), max=0x{max_v:02X}({max_v}), avg={avg_v:.1f}, count={len(pairs)}")

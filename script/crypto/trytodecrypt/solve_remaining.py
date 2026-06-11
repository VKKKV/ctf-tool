#!/usr/bin/env python3
"""
Comprehensive TryToDecrypt solver.
Tries multiple known algorithm patterns on each unsolved ciphertext.
"""
import string

CHARSET = string.digits + string.ascii_lowercase + string.ascii_uppercase + '-_.,;:?! '
# CHARSET length: 10 + 26 + 26 + 9 = 71

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

def hex_pairs(s):
    """Split hex string into pairs."""
    return [s[i:i+2] for i in range(0, len(s), 2)]

def hex_quads(s):
    """Split hex string into 4-char groups."""
    return [s[i:i+4] for i in range(0, len(s), 4)]

def dec_charset_index(val):
    """Get charset index from hex value (original Easy style)."""
    if 0 <= val < len(CHARSET):
        return CHARSET[val]
    return None

def dec_hard_encode(val):
    """Decode using Hard encoding scheme (0=00..9=09, a=0A..z=23, A=24..Z=3D, space=46, period=40)."""
    if val <= 0x09:
        return chr(ord('0') + val)
    elif 0x0A <= val <= 0x23:
        return chr(ord('a') + val - 0x0A)
    elif 0x24 <= val <= 0x3D:
        return chr(ord('A') + val - 0x24)
    elif val == 0x40:
        return '.'
    elif val == 0x46:
        return ' '
    # Special chars
    special = "-_.,;:?! "
    idx = val - 0x3E
    if 0 <= idx < len(special):
        return special[idx]
    return None

def try_method(name, dec_func, chunks_kind='pairs', **kwargs):
    """Try a decryption method on all texts."""
    print(f"\n=== {name} ===")
    for tid, ct in TEXTS.items():
        if chunks_kind == 'pairs':
            chunks = hex_pairs(ct)
        elif chunks_kind == 'quads':
            chunks = hex_quads(ct)
        elif chunks_kind == 'raw':
            chunks = [ct]
        
        result = dec_func(chunks, ct, **kwargs)
        if result:
            print(f"  Text {tid}: {result[:80]}")

# Method 1: Simple charset index (Easy style)
def m1_charset_index(chunks, ct):
    result = []
    for c in chunks:
        val = int(c, 16)
        ch = dec_charset_index(val)
        if ch:
            result.append(ch)
        else:
            result.append('?')
    return ''.join(result)

# Method 2: Hard encoding scheme
def m2_hard_encode(chunks, ct):
    result = []
    for c in chunks:
        val = int(c, 16)
        ch = dec_hard_encode(val)
        if ch:
            result.append(ch)
        else:
            result.append('?')
    return ''.join(result)

# Method 3: Hex decode and show as ASCII
def m3_hex_ascii(chunks, ct):
    try:
        return bytes.fromhex(ct).decode('ascii', errors='replace')
    except:
        return None

# Method 4: 4-char chunks, offset+encoded diff (like Hard 4/5)
def m4_offset_encode(chunks, ct):
    result = []
    for c in chunks:
        if len(c) == 4:
            offset = int(c[0:2], 16)
            encoded = int(c[2:4], 16)
            diff = (encoded - offset) & 0xFF
            ch = dec_hard_encode(diff)
            if ch:
                result.append(ch)
            else:
                result.append('?')
    return ''.join(result)

# Method 5: 4-char chunks, reverse (offset comes second)
def m5_encode_offset(chunks, ct):
    result = []
    for c in chunks:
        if len(c) == 4:
            encoded = int(c[0:2], 16)
            offset = int(c[2:4], 16)
            diff = (encoded - offset) & 0xFF
            ch = dec_hard_encode(diff)
            if ch:
                result.append(ch)
            else:
                result.append('?')
    return ''.join(result)

# Method 6: Split into first half and second half (key+data like Hard 5/6)
def m6_split_halves(chunks, ct):
    half = len(ct) // 2
    if half % 2 != 0:
        half -= half % 2
    first = ct[:half]
    second = ct[half:2*half]
    result = []
    for i in range(0, half, 2):
        a = int(first[i:i+2], 16)
        b = int(second[i:i+2], 16)
        diff = (a - b) & 0xFF
        ch = dec_hard_encode(diff)
        if ch:
            result.append(ch)
        else:
            result.append('?')
    return ''.join(result)

# Method 7: Same as Method 6 but reversed
def m7_split_halves_rev(chunks, ct):
    half = len(ct) // 2
    if half % 2 != 0:
        half -= half % 2
    first = ct[:half]
    second = ct[half:2*half]
    result = []
    for i in range(0, half, 2):
        a = int(first[i:i+2], 16)
        b = int(second[i:i+2], 16)
        diff = (b - a) & 0xFF
        ch = dec_hard_encode(diff)
        if ch:
            result.append(ch)
        else:
            result.append('?')
    return ''.join(result)

# Method 8: Try varions easy-style arithmetic
def m8_arithmetic(chunks, ct):
    """Try various arithmetic formulas on hex pairs."""
    results = {}
    for offset in range(-100, 101):
        result = []
        ok = True
        for c in chunks:
            val = int(c, 16)
            idx = (val - offset) % 256
            if 0 <= idx < len(CHARSET):
                result.append(CHARSET[idx])
            else:
                ok = False
                break
        if ok and len(result) == len(chunks):
            r = ''.join(result)
            if r and all(c in CHARSET for c in r):
                results[f"offset={offset}"] = r
    
    for k, v in list(results.items())[:5]:
        print(f"    {k}: {v}")
    return None

# Method 9: XOR-based
def m9_xor(chunks, ct):
    results = []
    for key in range(256):
        result = []
        ok = True
        for i, c in enumerate(chunks):
            val = int(c, 16)
            idx = val ^ key
            if 0 <= idx < len(CHARSET):
                result.append(CHARSET[idx])
            else:
                ok = False
                break
        if ok:
            r = ''.join(result)
            results.append(f"key=0x{key:02X}: {r}")
    return '\n'.join(results[:5])

# Method 10: Position-dependent XOR
def m10_pos_xor(chunks, ct):
    results = []
    for key_start in range(256):
        result = []
        ok = True
        for i, c in enumerate(chunks):
            val = int(c, 16)
            idx = val ^ ((key_start + i) & 0xFF)
            if 0 <= idx < len(CHARSET):
                result.append(CHARSET[idx])
            else:
                ok = False
                break
        if ok:
            r = ''.join(result)
            results.append(f"key_start=0x{key_start:02X}: {r}")
    return '\n'.join(results[:5])

# Run all methods
print("=" * 70)
print("TRYING ALL DECRYPTION METHODS ON ALL UNSOLVED TEXTS")
print("=" * 70)

# First, show basic properties
for tid in sorted(TEXTS.keys()):
    ct = TEXTS[tid]
    pairs = hex_pairs(ct)
    vals = [int(p, 16) for p in pairs]
    print(f"\n--- Text {tid} ---")
    print(f"  Length: {len(ct)} hex chars")
    print(f"  As pairs: {pairs}")
    print(f"  As values: {vals}")
    print(f"  Min/Max: {min(vals):#x}/{max(vals):#x}")

# Try specific methods
print("\n\n" + "=" * 70)
print("Method 1: Simple charset index (Easy style)")
print("=" * 70)
for tid in sorted(TEXTS.keys()):
    ct = TEXTS[tid]
    pairs = hex_pairs(ct)
    result = m1_charset_index(pairs, ct)
    print(f"  Text {tid}: {result}")

print("\n\n" + "=" * 70)
print("Method 2: Hard encoding scheme")
print("=" * 70)
for tid in sorted(TEXTS.keys()):
    ct = TEXTS[tid]
    pairs = hex_pairs(ct)
    result = m2_hard_encode(pairs, ct)
    print(f"  Text {tid}: {result}")

print("\n\n" + "=" * 70)
print("Method 3: Hex decode as ASCII")
print("=" * 70)
for tid in sorted(TEXTS.keys()):
    ct = TEXTS[tid]
    result = m3_hex_ascii(None, ct)
    if result:
        print(f"  Text {tid}: \"{result}\"")

print("\n\n" + "=" * 70)
print("Method 4: 4-char chunks, offset+encoded (Hard 4 style)")
print("=" * 70)
for tid in sorted(TEXTS.keys()):
    ct = TEXTS[tid]
    if len(ct) % 4 == 0:
        quads = hex_quads(ct)
        result = m4_offset_encode(quads, ct)
        print(f"  Text {tid}: {result}")

print("\n\n" + "=" * 70)
print("Method 5: 4-char chunks, encoded+offset (reversed)")
print("=" * 70)
for tid in sorted(TEXTS.keys()):
    ct = TEXTS[tid]
    if len(ct) % 4 == 0:
        quads = hex_quads(ct)
        result = m5_encode_offset(quads, ct)
        print(f"  Text {tid}: {result}")

print("\n\n" + "=" * 70)
print("Method 6: Split halves (Hard 5/6 style)")
print("=" * 70)
for tid in sorted(TEXTS.keys()):
    ct = TEXTS[tid]
    if len(ct) % 2 == 0:
        result = m6_split_halves(None, ct)
        print(f"  Text {tid}: {result}")

print("\n\n" + "=" * 70)
print("Method 7: Split halves reversed")
print("=" * 70)
for tid in sorted(TEXTS.keys()):
    ct = TEXTS[tid]
    if len(ct) % 2 == 0:
        result = m7_split_halves_rev(None, ct)
        print(f"  Text {tid}: {result}")

# Text 21 specific: double hex decode
print("\n\n" + "=" * 70)
print("TEXT 21 - Hex decode analysis")
print("=" * 70)
ct21 = TEXTS[21]
decoded21 = bytes.fromhex(ct21).decode('ascii')
print(f"  First decode: \"{decoded21}\"")
# Try to find a pattern in the decoded string
print(f"  Characters: {[c for c in decoded21]}")
print(f"  Ord values: {[ord(c) for c in decoded21]}")
# Could this be a URL?
if '/' in decoded21:
    print(f"  Contains '/': possible URL path")
# Could the digits be ASCII codes?
nums = []
current = ""
for c in decoded21:
    if c.isdigit():
        current += c
    else:
        if current:
            nums.append(int(current))
        current = c
if current:
    nums.append(int(current))
if nums:
    print(f"  Numbers found: {nums}")
    print(f"  As chars: {''.join(chr(n) if 32 <= n <= 126 else '?' for n in nums)}")

# Text 21: try interpreting pairs as hex of something else
print(f"\n  Pairs of decoded string:")
for i in range(0, len(decoded21), 2):
    chunk = decoded21[i:i+2]
    print(f"    '{chunk}'")

# Text 10 specific analysis
print("\n\n" + "=" * 70)
print("TEXT 10 - Detailed analysis")
print("=" * 70)
ct10 = TEXTS[10]
pairs10 = hex_pairs(ct10)
vals10 = [int(p, 16) for p in pairs10]
print(f"  Hex values: {[hex(v) for v in vals10]}")
print(f"  As charset indices: {[dec_charset_index(v) for v in vals10]}")

# Try arithmetic offsets
print(f"\n  Trying arithmetic formulas on Text 10:")
for offset in range(256):
    result = []
    ok = True
    for v in vals10:
        idx = (v - offset) & 0xFF
        ch = dec_charset_index(idx)
        if ch is None:
            ok = False
            break
        result.append(ch)
    if ok:
        r = ''.join(result)
        # Check if it looks like English
        print(f"    offset={offset:3d}: {r}")

# Try Text 11 with various approaches
print("\n\n" + "=" * 70)
print("TEXT 11 - First values analysis")
print("=" * 70)
ct11 = TEXTS[11]
pairs11 = hex_pairs(ct11[:40])  # First 20 pairs
# Note: ct11 has 81 chars, so last pair is incomplete
print(f"  First 20 hex values: {[int(p,16) for p in pairs11]}")
print(f"  First 10 pairs as str: {pairs11[:10]}")

# Try pairing differently if 81 chars
print(f"\n  Text 11 has odd length (81). Trying to fix:")
# Option: assume last char is extra or missing one
# Try dropping last char
ct11a = ct11[:-1]
pairs11a = hex_pairs(ct11a)
print(f"  Without last char ({len(ct11a)} chars): {len(pairs11a)} pairs")
# Try text6-style (add a 0 to make even)
ct11b = ct11 + '0'
pairs11b = hex_pairs(ct11b)
print(f"  With trailing 0 ({len(ct11b)} chars): {len(pairs11b)} pairs")
# Hard encode
result = m2_hard_encode(pairs11a, None)
print(f"  Hard encode (drop last): {result}")
result = m2_hard_encode(pairs11b, None)
print(f"  Hard encode (add 0): {result}")

# Text 13 specific: try the 4-char offset approach we discovered
print("\n\n" + "=" * 70)
print("TEXT 13 - Offset analysis (like Hard scheme)")
print("=" * 70)
ct13 = TEXTS[13]
quads13 = hex_quads(ct13)
print(f"  4-char chunks: {quads13}")
result = m4_offset_encode(quads13, ct13)
print(f"  offset+encoded: {result}")
result = m5_encode_offset(quads13, ct13)
print(f"  encoded+offset: {result}")

# Try reversing the 4-char chunks
rev_quads13 = quads13[::-1]
print(f"  Reversed chunks: {rev_quads13}")
result = m4_offset_encode(rev_quads13, ct13)
print(f"  Reversed offset+encoded: {result}")

# Text 14 analysis
print("\n\n" + "=" * 70)
print("TEXT 14 - Offset analysis")
print("=" * 70)
ct14 = TEXTS[14]
quads14 = hex_quads(ct14)
print(f"  4-char chunks: {quads14}")
result = m4_offset_encode(quads14, ct14)
print(f"  offset+encoded: {result}")
result = m5_encode_offset(quads14, ct14)
print(f"  encoded+offset: {result}")
rev_quads14 = quads14[::-1]
result = m4_offset_encode(rev_quads14, ct14)
print(f"  Reversed offset+encoded: {result}")

# Try split halves on Text 14
print(f"  Split halves (key-data): {m6_split_halves(None, ct14)}")
print(f"  Split halves reverse: {m7_split_halves_rev(None, ct14)}")

# Text 20 analysis
print("\n\n" + "=" * 70)
print("TEXT 20 - Offset analysis")
print("=" * 70)
ct20 = TEXTS[20]
quads20 = hex_quads(ct20)
print(f"  4-char chunks: {len(quads20)}")
result = m4_offset_encode(quads20, ct20)
print(f"  offset+encoded: {result}")
result = m5_encode_offset(quads20, ct20)
print(f"  encoded+offset: {result}")
print(f"  Split halves (key-data): {m6_split_halves(None, ct20)}")
print(f"  Split halves reverse: {m7_split_halves_rev(None, ct20)}")

# Text 22 analysis
print("\n\n" + "=" * 70)
print("TEXT 22 - Analysis")
print("=" * 70)
ct22 = TEXTS[22]
quads22 = hex_quads(ct22)
print(f"  4-char chunks: {len(quads22)}")
result = m4_offset_encode(quads22, ct22)
print(f"  offset+encoded: {result}")
result = m5_encode_offset(quads22, ct22)
print(f"  encoded+offset: {result}")
print(f"  Hard encode (pairs): {m2_hard_encode(hex_pairs(ct22), None)}")
print(f"  Split halves: {m6_split_halves(None, ct22)}")

# Text 23 analysis
print("\n\n" + "=" * 70)
print("TEXT 23 - Small chunk analysis")
print("=" * 70)
ct23 = TEXTS[23]
print(f"  First 20 hex values: {[int(ct23[i:i+2],16) for i in range(0,40,2)]}")
quads23 = hex_quads(ct23)
result4 = m4_offset_encode(quads23, ct23)
print(f"  offset+encoded (first 60 chars): {result4[:30] if result4 else 'N/A'}")
print(f"  Split halves: {m6_split_halves(None, ct23)[:50]}")

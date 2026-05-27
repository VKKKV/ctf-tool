#!/usr/bin/env python3

# Analyze Text 20 (Too Much 2)
ct20 = "8221E4F2173368D6B6B6E5050935D986A8C4CA764CF8A8C4B734E99807140B19DB691998095CC4E3D6C60D6E91"
print(f"Text 20 length: {len(ct20)} hex chars")
print(f"Text 20 length in bytes: {len(ct20)//2}")

# 5 hex per char, 90 hex chars = 18 chars
# First 18 hex chars = prefixes
# Next 72 hex chars = data (4 hex per char)

prefix20 = ct20[:18]
data20 = ct20[18:]
print(f"Prefix (18 hex): {prefix20}")
print(f"Prefix bytes: {[int(prefix20[i:i+2],16) for i in range(0,len(prefix20),2)]}")
print(f"Data (72 hex): {data20}")
print()

# 4 hex per char = 2 bytes per char
# The 2 bytes: offset and encrypted value
pairs20 = []
for i in range(0, len(data20), 4):
    offset = int(data20[i:i+2], 16)
    enc = int(data20[i+2:i+4], 16)
    pairs20.append((offset, enc))
    
print("Text 20 pairs (offset, encrypted):")
for idx, (off, enc) in enumerate(pairs20):
    diff = (enc - off) & 0xFF
    print(f"  [{idx}] offset={off:02X}, enc={enc:02X}, diff={diff:02X} ({diff})")

print()
print("="*60)

# Text 22 (Too Much 4)
ct22 = "00100401400A0120A101C0310F503706004E05B0870A00880D80ED0BE1262890FD16816A1453453721963ED1D11F04624D9"
print(f"\nText 22 length: {len(ct22)} hex chars")
print(f"Text 22 length in bytes: {len(ct22)//2}")

# Context says step seems to be 3 hex per char
# 98 hex chars -> not divisible by 3
# 0020 (length in bytes)? Let me count properly
print(f"ct22 hex chars count: {len(ct22)}")

# Let me try 3 hex per char
step22 = 3
try:
    if len(ct22) % step22 == 0:
        nchars22 = len(ct22) // step22
        print(f"With step {step22}: {nchars22} characters")
        for i in range(nchars22):
            val = ct22[i*step22:(i+1)*step22]
            print(f"  [{i}] {val}")
except:
    pass

# Try 2 hex per char
step22b = 2
if len(ct22) % step22b == 0:
    nchars22b = len(ct22) // step22b
    print(f"\nWith step {step22b}: {nchars22b} bytes")
    vals = [int(ct22[i*2:(i+1)*2],16) for i in range(nchars22b)]
    print(f"  Bytes: {[f'{v:02X}' for v in vals]}")

# Try 6 hex per char (like Text 19 structure)
step22c = 6
if len(ct22) % step22c == 0:
    nchars22c = len(ct22) // step22c
    print(f"\nWith step {step22c}: {nchars22c} characters")
    # First 2 hex = prefix, next 4 hex = 2 bytes (offset, enc)
    for i in range(nchars22c):
        prefix = ct22[i*step22c:i*step22c+2]
        pair = ct22[i*step22c+2:i*step22c+6]
        off = int(pair[0:2],16)
        enc = int(pair[2:4],16)
        diff = (enc - off) & 0xFF
        print(f"  [{i}] prefix={prefix}, offset={off:02X}, enc={enc:02X}, diff={diff:02X}")

print()
print("="*60)

# Text 23 (Too Much 5)
ct23 = "E3F59F001361B62958E551B9702F2C6B25F9E3FC350062295A1A20182041493C447BA0767A393A1F278DB14268565F51575C65212A8386494B383F7375676845472F30494C737A406890988B8D50577A835960476B6F73686E6367668B787A494C33357EA4555E191C18216A6F353A173E2026474A8A8C3F481416759D"
print(f"\nText 23 length: {len(ct23)} hex chars")
print(f"Text 23 length in bytes: {len(ct23)//2}")

# Try different step sizes
for step in [2, 3, 4, 5, 6, 10]:
    if len(ct23) % step == 0:
        nchars = len(ct23) // step
        print(f"  Step {step}: {nchars} 'chars'")

# Try 10 hex per char (5 bytes per char - like some Too Much patterns)
# Or maybe half is key, half is data (like hard mode)
half23 = len(ct23) // 4  # split in half by bytes
print(f"\n  Half length (in bytes): {half23}")
print(f"  Half (in hex): {len(ct23)//4}")
key23 = ct23[:len(ct23)//2]
data23 = ct23[len(ct23)//2:]
print(f"  First half (key?): {key23}")
print(f"  Second half (data?): {data23}")

# If first half = key (2 hex per char), second half = encrypted (2 hex per char)
# Then #chars = len(first_half_bytes) = len(ct23)//4
nchars23 = len(ct23)//4
print(f"\n  If split into key+data of 2 hex each: {nchars23} chars")
for i in range(min(nchars23, 20)):
    k = int(key23[i*2:i*2+2],16)
    d = int(data23[i*2:i*2+2],16)
    diff = (d - k) & 0xFF
    print(f"    [{i}] key={k:02X}, data={d:02X}, diff={diff:02X} ({diff})")

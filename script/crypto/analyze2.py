#!/usr/bin/env python3

ct19 = '0E0508000609060F070F0105568B8E901C436B6D84C7597F4D502F621B4D2669395E2E537981'
print(f'Text 19: {ct19}')
print(f'Length: {len(ct19)}')

# The too_much1.py script used: split_point = len(phrase) // 5
split = len(ct19) // 5
prefix = ct19[:split]
remaining = ct19[split:]
print(f'split={split}, prefix={prefix}')
print(f'remaining={remaining}, len={len(remaining)}')
print(f'Divisible by 4: {len(remaining) % 4 == 0}')

# Since it's not divisible, maybe the formula is different
# Let me try: what if the prefix is NOT included in the 5-part split?
# i.e., total = prefix_len + 4*num_chars where total = 76
# 76 = prefix_len + 4*num_chars
# If num_chars = 13, prefix_len = 76-52 = 24
# If num_chars = 14, prefix_len = 76-56 = 20
# If num_chars = 15, prefix_len = 76-60 = 16
# If num_chars = 16, prefix_len = 76-64 = 12
# If num_chars = 17, prefix_len = 76-68 = 8
# If num_chars = 18, prefix_len = 76-72 = 4

# From paulfrisby's solution, prefix = 0E0508000609060F (16 hex chars) = 8 bytes
# And 15 pairs = 30 bytes = 60 hex chars
# 16 + 60 = 76 ✓

# So the split is: first 16 hex chars = prefix, then 15 groups of 4 hex chars
# This means split_point = 16, not len//5
# So the too_much1.py script uses a DIFFERENT split approach

print('\n--- Trying split=16 ---')
prefix = ct19[:16]
data = ct19[16:]
print(f'prefix={prefix}')
print(f'data={data}')
print(f'Number of 4-hex groups: {len(data)//4}')

li = '0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ-_.,;:?! '
result = ''
for i in range(0, len(data), 4):
    a = int(data[i:i+2], 16)
    b = int(data[i+2:i+4], 16)
    diff = b - a
    if 0 <= diff < len(li):
        result += li[diff]
    else:
        result += f'[{diff}]'
print(f'result: {result}')

# Now let me analyze Text 20
ct20 = '8221E4F2173368D6B6B6E5050935D986A8C4CA764CF8A8C4B734E99807140B19DB691998095CC4E3D6C60D6E91'
print(f'\nText 20: {ct20}')
print(f'Length: {len(ct20)}')

# 90 hex chars
# For the too_much pattern: total = prefix_len + 4*num_chars
# 90 = prefix_len + 4*num_chars
# Options: prefix_len=10,num_chars=20; prefix_len=14,num_chars=19;
#          prefix_len=18,num_chars=18; prefix_len=22,num_chars=17;
#          prefix_len=26,num_chars=16; prefix_len=30,num_chars=15

# From context: "5 hex per char → 18 characters"
# 5*18 = 90 ✓
# So each char = 5 hex chars
# 5 = 1 prefix hex + 4 data hex
# So prefix_len = 18, data = 72 (18 groups of 4)

print('\n--- Trying split=18 ---')
prefix20 = ct20[:18]
data20 = ct20[18:]
print(f'prefix={prefix20}')
print(f'data={data20}')
print(f'Number of 4-hex groups: {len(data20)//4}')

result20 = ''
for i in range(0, len(data20), 4):
    a = int(data20[i:i+2], 16)
    b = int(data20[i+2:i+4], 16)
    diff = b - a
    if 0 <= diff < len(li):
        result20 += li[diff]
    else:
        result20 += f'[{diff}]'
print(f'result: {result20}')

# The diffs might not be valid - let me see what they are
print('\nDiffs:')
for i in range(0, len(data20), 4):
    a = int(data20[i:i+2], 16)
    b = int(data20[i+2:i+4], 16)
    diff = b - a
    print(f'  {data20[i:i+2]}-{data20[i+2:i+4]} = {diff} ({hex(diff)})', end='')
    if 0 <= diff < len(li):
        print(f' -> {li[diff]}')
    else:
        print(' [INVALID]')

# Try Text 21
ct21 = '333131353156333131323231305230363135315631333151342F3430313131323154342F'
print(f'\nText 21: {ct21}')
print(f'Length: {len(ct21)}')

# Simple hex decode?
try:
    decoded = bytes.fromhex(ct21).decode('utf-8', errors='replace')
    print(f'As ASCII: {decoded}')
except:
    print('Could not decode as ASCII')

# Text 22
ct22 = '00100401400A0120A101C0310F503706004E05B0870A00880D80ED0BE1262890FD16816A1453453721963ED1D11F04624D9'
print(f'\nText 22: {ct22}')
print(f'Length: {len(ct22)}')

# 99 hex chars
# Context says "step seems to be 3 hex per char"
# 99/3 = 33 chars
# Each 3-hex-char could be a direct index into the character set
print('\n--- With step=3 ---')
for i in range(0, len(ct22), 3):
    val = int(ct22[i:i+3], 16)
    if 0 <= val < len(li):
        print(f'  {ct22[i:i+3]} = {val} -> {li[val]}')
    else:
        print(f'  {ct22[i:i+3]} = {val} [OUT OF RANGE, max={len(li)-1}]')

# Let me also try step=4 or other
# 99 is not divisible by 2
# What about as a hex string representing something else?

# Text 23
ct23 = 'E3F59F001361B62958E551B9702F2C6B25F9E3FC350062295A1A20182041493C447BA0767A393A1F278DB14268565F51575C65212A8386494B383F7375676845472F30494C737A406890988B8D50577A835960476B6F73686E6367668B787A494C33357EA4555E191C18216A6F353A173E2026474A8A8C3F481416759D'
print(f'\nText 23: {ct23}')
print(f'Length: {len(ct23)}')

# Try hard mode style: split in half
half = len(ct23) // 2
key23 = ct23[:half]
data23 = ct23[half:]
print(f'\n--- Hard mode style (split in half) ---')
print(f'First half (key): {key23[:40]}...')
print(f'Second half (data): {data23[:40]}...')
print(f'Half len: {half}')

result23 = ''
for i in range(0, half, 2):
    k = int(key23[i:i+2], 16)
    d = int(data23[i:i+2], 16)
    diff = k - d  # key - data (like hard5/6)
    if 0 <= diff < len(li):
        result23 += li[diff]
    else:
        result23 += f'[{diff}]'
print(f'Result (key-data): {result23}')

# Try data - key
result23b = ''
for i in range(0, half, 2):
    k = int(key23[i:i+2], 16)
    d = int(data23[i:i+2], 16)
    diff = d - k  # data - key
    if 0 <= diff < len(li):
        result23b += li[diff]
    else:
        result23b += f'[{diff}]'
print(f'Result (data-key): {result23b}')

#!/usr/bin/env python3

ciphertext = "ÁẨĀǍẦĀẶẰẨǍĄẦẤĂẤĂĀȀẨȀẶǍẠẢĄẨÁÀẨĂĂĀȦẨẮĂẤȀȦĀĂẤÀẢẪẨĂẮẴĂĄẤĄẮĄẤẲȀẲAẶẲẮǍĂẨĄẦẤĂĂẦẲẮẪÁẴẨĂẮẢẨǍẨĀĂẠẴẮĄÀĀẠẴẨẠẲẮȦẨĄẦẨĀÁĀẶẦẨĂẨĄĄẤȀȦẮẢẠẲẮǍẶǍĀẶẰẨǍÁẲẤȀȦĄẦẤĂẴẠẦĀȀÁÀẤȦẦĄẴẨĀẪĂẲĀȀȀẲẠẤȀȦĄẦĀȀẰĂĄẲĄẦẨẪẲẲẰĀẪẤẰẨĂĄẦẨẶẦĀǍĀẶĄẨǍĂĀǍẨẮĄAĂẲẤĄĂĀẪĂẲĀẢǍẲẴẪẨÀĄẲẤÁẨȀĄẤAẠĄẦẨẴẠĄẨĂÀĀẠẴẨẪẨĄẮĂẰȀẲÄẤȀĄẦẨȂẲĄẨĂĀȀÁĂẲẪẮĄẤẲȀẴẲĀǍÁĀẴẲẮĄẠẲẮǍẨẬẢẨǍẤẨȀẶẨĀȀẠÄĀẠÁẢÀÁẪẢẶẴAẦȀĂẤĂẠẲẮǍĂẲẪẮĄẤẲȀ"

# Let me try to use a scoring system. Let me start with the xkcd mapping
# and then iteratively improve.

# Known xkcd mappings (pre-composed chars that match):
xkcd_map = {
    'A': 'A',  # U+0041
    'À': 'V',  # U+00C0
    'Á': 'E',  # U+00C1
    'Ä': 'U',  # U+00C4
    'Ā': 'T',  # U+0100
    'Ă': 'L',  # U+0102
    'Ǎ': 'M',  # U+01CD
    'Ȁ': 'W',  # U+0200
    'Ȃ': 'R',  # U+0202
    'Ȧ': 'B',  # U+0226
    'Ạ': 'K',  # U+1EA0
    'Ả': 'I',  # U+1EA2
}

# Ą (ogonek) - closest match to A̧ (cedilla) = C
xkcd_map['Ą'] = 'C'

# Now let's try to decode and see what English words we can spot
decoded = ''
for c in ciphertext:
    if c in xkcd_map:
        decoded += xkcd_map[c]
    else:
        decoded += '?'

print("Partial decode (known xkcd mappings):")
print(decoded)
print()

# Let me count which letters we have
from collections import Counter
letter_counts = Counter(decoded.replace('?', ''))
print("Decoded letter frequencies:")
for letter, count in letter_counts.most_common():
    print(f"  {letter}: {count}")

# Total decoded chars
total_decoded = sum(1 for c in decoded if c != '?')
total_unknown = sum(1 for c in decoded if c == '?')
print(f"\nDecoded: {total_decoded}/{total_decoded + total_unknown} chars ({total_unknown} unknown)")

# Let me look for word patterns.
# Common English words with only the known letters...
# Let me split the unknown characters and see what patterns emerge

print("\nShowing unknown chars with context:")
for i, c in enumerate(decoded):
    if c == '?':
        context_before = decoded[max(0,i-10):i]
        context_after = decoded[i+1:i+11]
        print(f"  pos {i}: ...{context_before}[?]{context_after}...")

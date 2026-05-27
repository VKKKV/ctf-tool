#!/usr/bin/env python3

ciphertext = "ÁẨĀǍẦĀẶẰẨǍĄẦẤĂẤĂĀȀẨȀẶǍẠẢĄẨÁÀẨĂĂĀȦẨẮĂẤȀȦĀĂẤÀẢẪẨĂẮẴĂĄẤĄẮĄẤẲȀẲAẶẲẮǍĂẨĄẦẤĂĂẦẲẮẪÁẴẨĂẮẢẨǍẨĀĂẠẴẮĄÀĀẠẴẨẠẲẮȦẨĄẦẨĀÁĀẶẦẨĂẨĄĄẤȀȦẮẢẠẲẮǍẶǍĀẶẰẨǍÁẲẤȀȦĄẦẤĂẴẠẦĀȀÁÀẤȦẦĄẴẨĀẪĂẲĀȀȀẲẠẤȀȦĄẦĀȀẰĂĄẲĄẦẨẪẲẲẰĀẪẤẰẨĂĄẦẨẶẦĀǍĀẶĄẨǍĂĀǍẨẮĄAĂẲẤĄĂĀẪĂẲĀẢǍẲẴẪẨÀĄẲẤÁẨȀĄẤAẠĄẦẨẴẠĄẨĂÀĀẠẴẨẪẨĄẮĂẰȀẲÄẤȀĄẦẨȂẲĄẨĂĀȀÁĂẲẪẮĄẤẲȀẴẲĀǍÁĀẴẲẮĄẠẲẮǍẨẬẢẨǍẤẨȀẶẨĀȀẠÄĀẠÁẢÀÁẪẢẶẴAẦȀĂẤĂẠẲẮǍĂẲẪẮĄẤẲȀ"

unique_chars = sorted(set(ciphertext))
char_to_label = {}
for i, c in enumerate(unique_chars):
    label = chr(ord('A') + i)
    char_to_label[c] = label

labels = ''.join(char_to_label[c] for c in ciphertext)

# Let me try a completely different approach.
# Let me look at the trigram "GOP" which appears 5 times.
# If we assume this is the most common English word "the", then G=T, O=H, P=E.
# 
# But wait, let me also look at "USH" (4 times) and "LUS" (4 times).
# 
# Let me think about what the message likely contains:
# "Congratulations you have solved this challenge the solution is XXXXX"
# or similar.

# Let me look for a different approach. Let me check if the ciphertext 
# could be a simple substitution based on the Unicode codepoint order.
# Maybe the first character in Unicode order maps to 'A', second to 'B', etc.?

# Let me check: what if the mapping is by Unicode order?
# The challenge says "23 different Unicode 'A' variant characters"
# and "each 'A'-variant maps to a different letter A-W"

# What if we just use the Unicode order as the mapping?
# First character in Unicode order -> 'A', second -> 'B', ... 23rd -> 'W'

# That would mean:
# 'A' (U+0041) -> A
# 'À' (U+00C0) -> B
# 'Á' (U+00C1) -> C
# 'Ä' (U+00C4) -> D
# 'Ā' (U+0100) -> E
# 'Ă' (U+0102) -> F
# 'Ą' (U+0104) -> G
# 'Ǎ' (U+01CD) -> H
# 'Ȁ' (U+0200) -> I
# 'Ȃ' (U+0202) -> J
# 'Ȧ' (U+0226) -> K
# 'Ạ' (U+1EA0) -> L
# 'Ả' (U+1EA2) -> M
# 'Ấ' (U+1EA4) -> N
# 'Ầ' (U+1EA6) -> O
# 'Ẩ' (U+1EA8) -> P
# 'Ẫ' (U+1EAA) -> Q
# 'Ậ' (U+1EAC) -> R
# 'Ắ' (U+1EAE) -> S
# 'Ằ' (U+1EB0) -> T
# 'Ẳ' (U+1EB2) -> U
# 'Ẵ' (U+1EB4) -> V
# 'Ặ' (U+1EB6) -> W

# This is what I've been using. But maybe the mapping is different.
# Let me try reading the decoded text with this identity mapping
# (i.e., the label letter IS the plaintext letter).

# Wait, that's what we've been doing - the labels just represent which
# Unicode variant appears. The mapping from label (A-W) to plaintext 
# letter is what we need to find.

# Let me try a different ordering. What if the assignment isn't by Unicode
# order but by the order in which they first appear in the ciphertext?

# First occurrence order:
first_occurrence = {}
for i, c in enumerate(ciphertext):
    if c not in first_occurrence:
        first_occurrence[c] = i

first_order = sorted(first_occurrence.keys(), key=lambda c: first_occurrence[c])
print("Characters in first occurrence order:")
for i, c in enumerate(first_order):
    label = chr(ord('A') + i)
    print(f"  {i}: '{c}' (U+{ord(c):04X}) -> {label}")

# Let me try this ordering
char_to_label2 = {}
for i, c in enumerate(first_order):
    label = chr(ord('A') + i)
    char_to_label2[c] = label

labels2 = ''.join(char_to_label2[c] for c in ciphertext)
print(f"\nLabels (first occurrence order):")
print(labels2)

# Frequency with this ordering
freq2 = {}
for c in labels2:
    if c not in freq2:
        freq2[c] = 0
    freq2[c] += 1

print(f"\nLabel frequencies (first occurrence order):")
for c, count in sorted(freq2.items(), key=lambda x: -x[1]):
    print(f"  {c}: {count}")

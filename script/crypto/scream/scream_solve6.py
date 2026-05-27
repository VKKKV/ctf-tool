#!/usr/bin/env python3

ciphertext = "ÁẨĀǍẦĀẶẰẨǍĄẦẤĂẤĂĀȀẨȀẶǍẠẢĄẨÁÀẨĂĂĀȦẨẮĂẤȀȦĀĂẤÀẢẪẨĂẮẴĂĄẤĄẮĄẤẲȀẲAẶẲẮǍĂẨĄẦẤĂĂẦẲẮẪÁẴẨĂẮẢẨǍẨĀĂẠẴẮĄÀĀẠẴẨẠẲẮȦẨĄẦẨĀÁĀẶẦẨĂẨĄĄẤȀȦẮẢẠẲẮǍẶǍĀẶẰẨǍÁẲẤȀȦĄẦẤĂẴẠẦĀȀÁÀẤȦẦĄẴẨĀẪĂẲĀȀȀẲẠẤȀȦĄẦĀȀẰĂĄẲĄẦẨẪẲẲẰĀẪẤẰẨĂĄẦẨẶẦĀǍĀẶĄẨǍĂĀǍẨẮĄAĂẲẤĄĂĀẪĂẲĀẢǍẲẴẪẨÀĄẲẤÁẨȀĄẤAẠĄẦẨẴẠĄẨĂÀĀẠẴẨẪẨĄẮĂẰȀẲÄẤȀĄẦẨȂẲĄẨĂĀȀÁĂẲẪẮĄẤẲȀẴẲĀǍÁĀẴẲẮĄẠẲẮǍẨẬẢẨǍẤẨȀẶẨĀȀẠÄĀẠÁẢÀÁẪẢẶẴAẦȀĂẤĂẠẲẮǍĂẲẪẮĄẤẲȀ"

unique_chars = sorted(set(ciphertext))
char_to_label = {}
label_to_char = {}
for i, c in enumerate(unique_chars):
    label = chr(ord('A') + i)
    char_to_label[c] = label
    label_to_char[label] = c

labels = ''.join(char_to_label[c] for c in ciphertext)

# Let me try a different approach. Let me look for the pattern of "the" 
# by looking at common words that might appear.

# First, let me identify ALL patterns that repeat, and try to match them to words.

# Let me look at what BELVP could be. It appears at positions 90 and 238.
# BELVP = B E L V P
# This could be "THERE" (T H E R E) or "WHERE" (W H E R E) or something.

# What about "EWTPH" at positions 5 and 124?
# E W T P H
# If P = E, then EWTEH or something.

# Let me try yet another approach. Let me use constraint propagation.

# First guess: The most frequent label (P, 35 times) = E
# Second guess: The second most frequent (G or F, 29 times) = T or A

# Let me try P=E, G=T, and see what fits.

mapping = {}
mapping['P'] = 'E'  # most frequent = E

# Let me look at what "G" could be. G is very frequent (29). Could be T or A.
# Let me try G = T first (T is 2nd most common English letter).

# If P=E and G=T, then what about GOP?
# G O P = T O E. Could this be "THE"? Yes! If O=H.
# So GOP = THE, with G=T, O=H, P=E.

mapping['G'] = 'T'
mapping['O'] = 'H'

# Now let me decode and see what words we can spot
decoded = ''
for c in labels:
    if c in mapping:
        decoded += mapping[c]
    else:
        decoded += '_'

print("With P=E, G=T, O=H:")
print(labels)
print(decoded)
print()

# Now I need to figure out NIK (4 occurrences).
# N I K -> with current mapping, all unknown.
# Could be "ING" (N=I, I=N, K=G) or "AND" (N=A, I=N, K=D)

# Let me look at "ONF" (3 occurrences)
# O N F -> H _ _ 
# If "ONF" = "H__" - could be "HIS", "HER", "HAS", "HAD"

# Let me look at "USH" (4 occurrences, at positions 61, 119, 284, 318)
# U S H -> with current mapping, all unknown

# Let me look at "LUS" (4 occurrences, positions 95, 118, 283, 317)
# L U S -> all unknown

# The text has no spaces. But we know English words. 
# Let me look at the very beginning: "CPEHOEWTPH"
# C _ E _ H _ _ _ E T P H
# Wait, with current mapping:
# C _ E _ H _ _ _ E T E H
# Actually, labels: C P E H O E W T P H
# With mapping: C E ? E H ? ? T E ?
# C=?, P=E, E=?, H=?, O=H, E=?, W=?, T=?, P=E, H=?
# So: C ? ? ? H ? ? T E ?

# Hmm, this is confusing. Let me just print the decoding more carefully.

# Let me create a more readable format
def decode_with_mapping(labels, mapping):
    result = ''
    for c in labels:
        if c in mapping:
            result += mapping[c]
        else:
            result += c.lower()  # show the label letter in lowercase as placeholder
    return result

result = decode_with_mapping(labels, mapping)
print(result)

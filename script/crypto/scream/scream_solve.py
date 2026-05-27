#!/usr/bin/env python3

ciphertext = "ÁẨĀǍẦĀẶẰẨǍĄẦẤĂẤĂĀȀẨȀẶǍẠẢĄẨÁÀẨĂĂĀȦẨẮĂẤȀȦĀĂẤÀẢẪẨĂẮẴĂĄẤĄẮĄẤẲȀẲAẶẲẮǍĂẨĄẦẤĂĂẦẲẮẪÁẴẨĂẮẢẨǍẨĀĂẠẴẮĄÀĀẠẴẨẠẲẮȦẨĄẦẨĀÁĀẶẦẨĂẨĄĄẤȀȦẮẢẠẲẮǍẶǍĀẶẰẨǍÁẲẤȀȦĄẦẤĂẴẠẦĀȀÁÀẤȦẦĄẴẨĀẪĂẲĀȀȀẲẠẤȀȦĄẦĀȀẰĂĄẲĄẦẨẪẲẲẰĀẪẤẰẨĂĄẦẨẶẦĀǍĀẶĄẨǍĂĀǍẨẮĄAĂẲẤĄĂĀẪĂẲĀẢǍẲẴẪẨÀĄẲẤÁẨȀĄẤAẠĄẦẨẴẠĄẨĂÀĀẠẴẨẪẨĄẮĂẰȀẲÄẤȀĄẦẨȂẲĄẨĂĀȀÁĂẲẪẮĄẤẲȀẴẲĀǍÁĀẴẲẮĄẠẲẮǍẨẬẢẨǍẤẨȀẶẨĀȀẠÄĀẠÁẢÀÁẪẢẶẴAẦȀĂẤĂẠẲẮǍĂẲẪẮĄẤẲȀ"

# Get unique chars sorted by Unicode codepoint
unique_chars = sorted(set(ciphertext))
print(f"Total unique chars: {len(unique_chars)}")

# Map each unique char to a placeholder letter A-W (in Unicode order)
char_to_label = {}
label_to_char = {}
for i, c in enumerate(unique_chars):
    label = chr(ord('A') + i)
    char_to_label[c] = label
    label_to_char[label] = c

# Convert ciphertext to labels
labels = ''.join(char_to_label[c] for c in ciphertext)
print(f"\nCiphertext as labels (A-W):")
print(labels)

# Frequency of labels
freq = {}
for c in labels:
    if c not in freq:
        freq[c] = 0
    freq[c] += 1

print(f"\nLabel frequencies:")
for c, count in sorted(freq.items(), key=lambda x: -x[1]):
    print(f"  {c}: {count}")

# Show character-to-label mapping
print(f"\nChar to Label mapping (Unicode order):")
for c in unique_chars:
    print(f"  '{c}' (U+{ord(c):04X}) -> {char_to_label[c]}")

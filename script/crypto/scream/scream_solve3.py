#!/usr/bin/env python3

ciphertext = "ÁẨĀǍẦĀẶẰẨǍĄẦẤĂẤĂĀȀẨȀẶǍẠẢĄẨÁÀẨĂĂĀȦẨẮĂẤȀȦĀĂẤÀẢẪẨĂẮẴĂĄẤĄẮĄẤẲȀẲAẶẲẮǍĂẨĄẦẤĂĂẦẲẮẪÁẴẨĂẮẢẨǍẨĀĂẠẴẮĄÀĀẠẴẨẠẲẮȦẨĄẦẨĀÁĀẶẦẨĂẨĄĄẤȀȦẮẢẠẲẮǍẶǍĀẶẰẨǍÁẲẤȀȦĄẦẤĂẴẠẦĀȀÁÀẤȦẦĄẴẨĀẪĂẲĀȀȀẲẠẤȀȦĄẦĀȀẰĂĄẲĄẦẨẪẲẲẰĀẪẤẰẨĂĄẦẨẶẦĀǍĀẶĄẨǍĂĀǍẨẮĄAĂẲẤĄĂĀẪĂẲĀẢǍẲẴẪẨÀĄẲẤÁẨȀĄẤAẠĄẦẨẴẠĄẨĂÀĀẠẴẨẪẨĄẮĂẰȀẲÄẤȀĄẦẨȂẲĄẨĂĀȀÁĂẲẪẮĄẤẲȀẴẲĀǍÁĀẴẲẮĄẠẲẮǍẨẬẢẨǍẤẨȀẶẨĀȀẠÄĀẠÁẢÀÁẪẢẶẴAẦȀĂẤĂẠẲẮǍĂẲẪẮĄẤẲȀ"

unique_chars = sorted(set(ciphertext))
char_to_label = {}
for i, c in enumerate(unique_chars):
    label = chr(ord('A') + i)
    char_to_label[c] = label

labels = ''.join(char_to_label[c] for c in ciphertext)

# Find positions of 'A' (plain Latin A)
print("Positions where plain 'A' appears:")
for i, c in enumerate(ciphertext):
    if c == 'A':
        print(f"  Position {i}: context ...{ciphertext[max(0,i-5):i+6]}... -> ...{labels[max(0,i-5):i+6]}...")

# Let me also look for patterns that might be "the"
# "the" is a very common word. In our label system, it would be 3 characters.
# Let me look at what 3-grams are most frequent

from collections import Counter
trigrams = Counter()
for i in range(len(labels) - 2):
    trigrams[labels[i:i+3]] += 1

print("\nMost common trigrams:")
for tri, count in trigrams.most_common(20):
    print(f"  '{tri}': {count}")

# Let me also try to guess what "congratulations" might look like
# It's a long word, let me scan for patterns
# "congratulations" = 16 letters
# Let me look at the full label text in groups

print(f"\nFull label text ({len(labels)} chars):")
print(labels)
print()

# Let me print it in readable chunks
for i in range(0, len(labels), 60):
    print(f"{i:4d}: {labels[i:i+60]}")

#!/usr/bin/env python3

ciphertext = "ÁẨĀǍẦĀẶẰẨǍĄẦẤĂẤĂĀȀẨȀẶǍẠẢĄẨÁÀẨĂĂĀȦẨẮĂẤȀȦĀĂẤÀẢẪẨĂẮẴĂĄẤĄẮĄẤẲȀẲAẶẲẮǍĂẨĄẦẤĂĂẦẲẮẪÁẴẨĂẮẢẨǍẨĀĂẠẴẮĄÀĀẠẴẨẠẲẮȦẨĄẦẨĀÁĀẶẦẨĂẨĄĄẤȀȦẮẢẠẲẮǍẶǍĀẶẰẨǍÁẲẤȀȦĄẦẤĂẴẠẦĀȀÁÀẤȦẦĄẴẨĀẪĂẲĀȀȀẲẠẤȀȦĄẦĀȀẰĂĄẲĄẦẨẪẲẲẰĀẪẤẰẨĂĄẦẨẶẦĀǍĀẶĄẨǍĂĀǍẨẮĄAĂẲẤĄĂĀẪĂẲĀẢǍẲẴẪẨÀĄẲẤÁẨȀĄẤAẠĄẦẨẴẠĄẨĂÀĀẠẴẨẪẨĄẮĂẰȀẲÄẤȀĄẦẨȂẲĄẨĂĀȀÁĂẲẪẮĄẤẲȀẴẲĀǍÁĀẴẲẮĄẠẲẮǍẨẬẢẨǍẤẨȀẶẨĀȀẠÄĀẠÁẢÀÁẪẢẶẴAẦȀĂẤĂẠẲẮǍĂẲẪẮĄẤẲȀ"

unique_chars = sorted(set(ciphertext))
char_to_label = {}
for i, c in enumerate(unique_chars):
    label = chr(ord('A') + i)
    char_to_label[c] = label

labels = ''.join(char_to_label[c] for c in ciphertext)

# Let me look at the full label text to identify patterns
print("Label text:")
print(labels)
print()

# Let me count word lengths by looking at spaces (but there are no spaces)
# The challenge says punctuation has been removed. So words are concatenated.
# Let me try to find repeated patterns that might be common words.

# Find all substrings of length 2-10 and their positions
from collections import defaultdict

for length in [2, 3, 4, 5]:
    substrings = defaultdict(list)
    for i in range(len(labels) - length + 1):
        sub = labels[i:i+length]
        substrings[sub].append(i)
    
    # Show repeated substrings
    repeated = {k: v for k, v in substrings.items() if len(v) > 1}
    if repeated:
        print(f"\nRepeated {length}-grams:")
        for sub, positions in sorted(repeated.items(), key=lambda x: -len(x[1])):
            print(f"  '{sub}': positions {positions}")

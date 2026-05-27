# Scream! challenge - analyze the ciphertext

ciphertext = "ÁẨĀǍẦĀẶẰẨǍĄẦẤĂẤĂĀȀẨȀẶǍẠẢĄẨÁÀẨĂĂĀȦẨẮĂẤȀȦĀĂẤÀẢẪẨĂẮẴĂĄẤĄẮĄẤẲȀẲAẶẲẮǍĂẨĄẦẤĂĂẦẲẮẪÁẴẨĂẮẢẨǍẨĀĂẠẴẮĄÀĀẠẴẨẠẲẮȦẨĄẦẨĀÁĀẶẦẨĂẨĄĄẤȀȦẮẢẠẲẮǍẶǍĀẶẰẨǍÁẲẤȀȦĄẦẤĂẴẠẦĀȀÁÀẤȦẦĄẴẨĀẪĂẲĀȀȀẲẠẤȀȦĄẦĀȀẰĂĄẲĄẦẨẪẲẲẰĀẪẤẰẨĂĄẦẨẶẦĀǍĀẶĄẨǍĂĀǍẨẮĄAĂẲẤĄĂĀẪĂẲĀẢǍẲẴẪẨÀĄẲẤÁẨȀĄẤAẠĄẦẨẴẠĄẨĂÀĀẠẴẨẪẨĄẮĂẰȀẲÄẤȀĄẦẨȂẲĄẨĂĀȀÁĂẲẪẮĄẤẲȀẴẲĀǍÁĀẴẲẮĄẠẲẮǍẨẬẢẨǍẤẨȀẶẨĀȀẠÄĀẠȀẴǍẦẲÁȀẶÁAÀẨẤĂẠẲẮǍĂẲẪẮĄẤẲȀ"

print(f"Ciphertext length: {len(ciphertext)}")
print()

# Get unique characters
unique_chars = sorted(set(ciphertext))
print(f"Unique characters: {len(unique_chars)}")
for c in unique_chars:
    print(f"  U+{ord(c):04X} {c}  ({repr(c)})")

print()
print("Character frequencies:")
from collections import Counter
freq = Counter(ciphertext)
for char, count in freq.most_common():
    print(f"  {char} (U+{ord(char):04X}): {count}")

# English letter frequencies (most common to least)
# ETAOINSHRDLUCMWFGYPBVKJXQZ
english_freq = ['E', 'T', 'A', 'O', 'I', 'N', 'S', 'H', 'R', 'D', 'L', 'U', 'C', 'M', 'W', 'F', 'G', 'Y', 'P', 'B', 'V', 'K', 'J', 'X', 'Q', 'Z']

# Let's try a simple frequency mapping
# Map most frequent cipher chars to most frequent English letters
sorted_chars = [c for c, _ in freq.most_common()]
mapping = {}
for i, c in enumerate(sorted_chars):
    if i < len(english_freq):
        mapping[c] = english_freq[i]

decoded = ''.join(mapping.get(c, c) for c in ciphertext)
print(f"\nSimple frequency mapping (most frequent chars -> ETAOIN...):")
print(decoded)

# The message mentions the solution is bound to session id
# So likely the decoded message says something like "your solution is XXXXXX"
# Let me try a different approach - look for common words

# Let's also print positions of 'A' in the ciphertext
print("\n'Á' characters at positions:", [i for i, c in enumerate(ciphertext) if c == 'Á'])

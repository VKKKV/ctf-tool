import random
import re
from collections import Counter

ciphertext = "ÁẨĀǍẦĀẶẰẨǍĄẦẤĂẤĂĀȀẨȀẶǍẠẢĄẨÁÀẨĂĂĀȦẨẮĂẤȀȦĀĂẤÀẢẪẨĂẮẴĂĄẤĄẮĄẤẲȀẲAẶẲẮǍĂẨĄẦẤĂĂẦẲẮẪÁẴẨĂẮẢẨǍẨĀĂẠẴẮĄÀĀẠẴẨẠẲẮȦẨĄẦẨĀÁĀẶẦẨĂẨĄĄẤȀȦẮẢẠẲẮǍẶǍĀẶẰẨǍÁẲẤȀȦĄẦẤĂẴẠẦĀȀÁÀẤȦẦĄẴẨĀẪĂẲĀȀȀẲẠẤȀȦĄẦĀȀẰĂĄẲĄẦẨẪẲẲẰĀẪẤẰẨĂĄẦẨẶẦĀǍĀẶĄẨǍĂĀǍẨẮĄAĂẲẤĄĂĀẪĂẲĀẢǍẲẴẪẨÀĄẲẤÁẨȀĄẤAẠĄẦẨẴẠĄẨĂÀĀẠẴẨẪẨĄẮĂẰȀẲÄẤȀĄẦẨȂẲĄẨĂĀȀÁĂẲẪẮĄẤẲȀẴẲĀǍÁĀẴẲẮĄẠẲẮǍẨẬẢẨǍẤẨȀẶẨĀȀẠÄĀẠȀẴǍẦẲÁȀẶÁAÀẨẤĂẠẲẮǍĂẲẪẮĄẤẲȀ"

# Get unique ciphertext characters
unique_chars = sorted(set(ciphertext))
print(f"Unique chars: {len(unique_chars)}")

# Let me first try a simple frequency analysis approach
# English quadgram statistics for scoring
# We'll build a simple scoring system

# English letter frequencies (from most to least common)
# ETAOINSHRDLCUMWFGYPBVKJXQZ

# Let me try mapping by frequency order
freq = Counter(ciphertext)
sorted_by_freq = [c for c, _ in freq.most_common()]

# Map to English letters by frequency
eng_freq = ['E', 'T', 'A', 'O', 'I', 'N', 'S', 'H', 'R', 'D', 'L', 'C', 'U', 'M', 'W', 'F', 'G', 'Y', 'P', 'B', 'V', 'K', 'J']
# We have 23 unique chars, so we skip X, Q, Z (the least common English letters)

mapping = {}
for i, c in enumerate(sorted_by_freq):
    mapping[c] = eng_freq[i]

decoded = ''.join(mapping.get(c, '?') for c in ciphertext)
print("\nFrequency-based mapping (no spaces):")
print(decoded)
print()

# Let's try with spaces - maybe 'A' (plain A) is a space
# Actually, let me check what A maps to in frequency order
print(f"Plain 'A' (U+0041) frequency rank: {sorted_by_freq.index('A') if 'A' in sorted_by_freq else 'N/A'}")
print(f"Plain 'A' maps to: {mapping.get('A', '?')}")

# Hmm, 'A' maps to 'J' - that seems unlikely for a frequent word separator
# Let me try a different approach

# The challenge text might be something like "congratulations the solution is XXXXXX"
# or "well done your password is XXXXXX"
# Let me look for common English words

# Let me try a quadgram-based solver
# For this, I need English quadgram frequencies

# Let me use a simple approach: n-gram fitness
# I'll score the decoded text by looking at common English patterns

# First, let me look at what the message might contain
# The challenge says "The challenge solution is bound to your WeChall session id."
# So the decoded message should reveal a password/solution

# Let me look at the end of the message - often the last word/s is the solution
print("Last 20 cipher chars:", repr(ciphertext[-20:]))

# Let me try another frequency approach
# Instead of strict frequency mapping, let me try to find "THE" first
# ĄẦẨ appears 5 times as the most common trigram
# If ĄẦẨ = THE, then Ą=T, Ầ=H, Ẩ=E

# Let me also try "and" as "ẤȀȦ" (4 times)
# Ấ=A, Ȁ=N, Ȧ=D

# With these initial mappings, let me see if we can find more patterns
mapping2 = {'Ą': 'T', 'Ầ': 'H', 'Ẩ': 'E', 'Ấ': 'A', 'Ȁ': 'N', 'Ȧ': 'D'}
decoded2 = ''.join(mapping2.get(c, f'[{ord(c):04X}]') for c in ciphertext)
print("\nWith ĄẦẨ=THE and ẤȀȦ=AND:")
print(decoded2)
print()

# Look at "ẲẮǍ" (4 times) - could be "THA" "ING" "ENT" "ION" "AND" "FOR" etc.
# "ẠẲẮ" (4 times) - another common trigram

# If ẲẮǍ is "ING" or "ION" or "ENT"...
# Let's try various possibilities


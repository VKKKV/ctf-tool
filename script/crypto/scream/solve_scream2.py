ciphertext = "ÁẨĀǍẦĀẶẰẨǍĄẦẤĂẤĂĀȀẨȀẶǍẠẢĄẨÁÀẨĂĂĀȦẨẮĂẤȀȦĀĂẤÀẢẪẨĂẮẴĂĄẤĄẮĄẤẲȀẲAẶẲẮǍĂẨĄẦẤĂĂẦẲẮẪÁẴẨĂẮẢẨǍẨĀĂẠẴẮĄÀĀẠẴẨẠẲẮȦẨĄẦẨĀÁĀẶẦẨĂẨĄĄẤȀȦẮẢẠẲẮǍẶǍĀẶẰẨǍÁẲẤȀȦĄẦẤĂẴẠẦĀȀÁÀẤȦẦĄẴẨĀẪĂẲĀȀȀẲẠẤȀȦĄẦĀȀẰĂĄẲĄẦẨẪẲẲẰĀẪẤẰẨĂĄẦẨẶẦĀǍĀẶĄẨǍĂĀǍẨẮĄAĂẲẤĄĂĀẪĂẲĀẢǍẲẴẪẨÀĄẲẤÁẨȀĄẤAẠĄẦẨẴẠĄẨĂÀĀẠẴẨẪẨĄẮĂẰȀẲÄẤȀĄẦẨȂẲĄẨĂĀȀÁĂẲẪẮĄẤẲȀẴẲĀǍÁĀẴẲẮĄẠẲẮǍẨẬẢẨǍẤẨȀẶẨĀȀẠÄĀẠȀẴǍẦẲÁȀẶÁAÀẨẤĂẠẲẮǍĂẲẪẮĄẤẲȀ"

unique_chars = sorted(set(ciphertext))
print(f"Total characters: {len(ciphertext)}")
print(f"Unique characters: {len(unique_chars)}")

# Print the ciphertext grouped by potential word boundaries
# Since it's english without punctuation, let's see if there are any repeats that suggest common words

# Let's look at n-gram frequencies
from collections import Counter

# bigrams
bigrams = Counter()
for i in range(len(ciphertext)-1):
    bigrams[ciphertext[i:i+2]] += 1

print("\nMost common bigrams:")
for bg, cnt in bigrams.most_common(20):
    print(f"  {bg}: {cnt}")

# trigrams
trigrams = Counter()
for i in range(len(ciphertext)-2):
    trigrams[ciphertext[i:i+3]] += 1

print("\nMost common trigrams:")
for tg, cnt in trigrams.most_common(20):
    print(f"  {tg}: {cnt}")

# 4-grams
fourgrams = Counter()
for i in range(len(ciphertext)-3):
    fourgrams[ciphertext[i:i+4]] += 1

print("\nMost common 4-grams:")
for fg, cnt in fourgrams.most_common(20):
    print(f"  {fg}: {cnt}")

# Check if there's a known pattern - maybe the password is something embedded
# Look for the phrase "solution is" or "password is"
# If I map: the most frequent char to 'E', second to 'T', etc. and print
print("\n\n=== Frequency analysis ===")
freq = Counter(ciphertext)
print("Character frequency order (most to least):")
for c, cnt in freq.most_common():
    pct = cnt / len(ciphertext) * 100
    print(f"  {c} (U+{ord(c):04X}): {cnt:3d} ({pct:.1f}%)")

# English letter frequencies: E(12.7%) T(9.1%) A(8.2%) O(7.5%) I(7.0%) N(6.7%) S(6.3%) H(6.1%) R(6.0%) D(4.3%) L(4.0%) C(2.8%) U(2.8%) M(2.5%) W(2.4%) F(2.2%) G(2.0%) Y(2.0%) P(1.9%) B(1.5%) V(1.0%) K(0.8%) J(0.15%) X(0.15%) Q(0.10%) Z(0.07%)

# Let's try to see if we can figure out the mapping using known patterns
# The solution is session-bound, so the decoded message probably says something like
# "the solution is XXXXXX" or "your password is XXXXXX"

# Let's look for common patterns by trying to map
# First, let's see what the plaintext might look like if we guess "the" or "that" or "your"
# Common English words: the, and, that, have, this, with, your, from, they, was, for, are

# The most common trigram in English is "THE"
print("\n\nMost common trigram in ciphertext:", trigrams.most_common(1)[0])
# If that maps to "THE", we get a relationship

# Let's also think about what the solution might say:
# "Hello hacker this is a training challenge for simple substitution with an additional problem..."
# or 
# "Congratulations the password is XXXXXX"
# or
# "The solution to this challenge is XXXXXX"

# Let me try to identify word boundaries. In English without spaces, 
# common patterns like THIS, THAT, THE, AND, etc. can help


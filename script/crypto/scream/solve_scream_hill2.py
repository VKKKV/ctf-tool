"""
Substitution cipher solver using hill climbing with quadgram scoring.
"""
import random
import string
from collections import Counter

# English quadgram frequencies (from practicalcryptography.com)
# I'll use a simple approximation based on common English patterns

ciphertext = "ÁẨĀǍẦĀẶẰẨǍĄẦẤĂẤĂĀȀẨȀẶǍẠẢĄẨÁÀẨĂĂĀȦẨẮĂẤȀȦĀĂẤÀẢẪẨĂẮẴĂĄẤĄẮĄẤẲȀẲAẶẲẮǍĂẨĄẦẤĂĂẦẲẮẪÁẴẨĂẮẢẨǍẨĀĂẠẴẮĄÀĀẠẴẨẠẲẮȦẨĄẦẨĀÁĀẶẦẨĂẨĄĄẤȀȦẮẢẠẲẮǍẶǍĀẶẰẨǍÁẲẤȀȦĄẦẤĂẴẠẦĀȀÁÀẤȦẦĄẴẨĀẪĂẲĀȀȀẲẠẤȀȦĄẦĀȀẰĂĄẲĄẦẨẪẲẲẰĀẪẤẰẨĂĄẦẨẶẦĀǍĀẶĄẨǍĂĀǍẨẮĄAĂẲẤĄĂĀẪĂẲĀẢǍẲẴẪẨÀĄẲẤÁẨȀĄẤAẠĄẦẨẴẠĄẨĂÀĀẠẴẨẪẨĄẮĂẰȀẲÄẤȀĄẦẨȂẲĄẨĂĀȀÁĂẲẪẮĄẤẲȀẴẲĀǍÁĀẴẲẮĄẠẲẮǍẨẬẢẨǍẤẨȀẶẨĀȀẠÄĀẠȀẴǍẦẲÁȀẶÁAÀẨẤĂẠẲẮǍĂẲẪẮĄẤẲȀ"

# Get unique chars
unique_chars = sorted(set(ciphertext))
print(f"Number of unique ciphertext chars: {len(unique_chars)}")

# Let me try yet another approach - look at this systematically
# First, let me figure out if there are spaces or word boundaries
# by looking at the character at the start

# The first 20 chars
print("First 20:", repr(ciphertext[:20]))
print("Last 20:", repr(ciphertext[-20:]))

# Let me try to use the official xkcd scream cipher library
# or implement the mapping

# Actually, let me re-examine the challenge more carefully
# The challenge says "I stole this cipher from the internets"
# This strongly suggests it's the xkcd scream cipher

# But the characters in the ciphertext include Vietnamese compound chars
# that aren't in the standard xkcd mapping

# Let me check if there's a simple mapping between Vietnamese A variants
# and English letters based on something systematic

# The Vietnamese A variants can be categorized by:
# 1. Base: A, Ă (breve), Â (circumflex) 
# 2. Tone: none, acute (´), grave (`), hook (̉), tilde (̃), dot below (̣)

# With A base: A, À, Á, Ả, Ã, Ạ (but Ã is missing from ciphertext)
# With Ă base: Ă, Ằ, Ắ, Ẳ, Ẵ, Ặ
# With Â base: Â, Ầ, Ấ, Ẩ, Ẫ, Ậ (but Â is missing from ciphertext)

# The ciphertext has A, À, Á, Ả, Ạ (but no Ã!)
# And Ă, Ằ, Ắ, Ẳ, Ẵ, Ặ
# And Ầ, Ấ, Ẩ, Ẫ, Ậ (but no Â!)

# Plus: Ā, Ą, Ǎ, Ȁ, Ȃ, Ȧ, Ä (these are single-diacritic A's)

# So the full set of 23 chars:
# A, À, Á, Ä, Ā, Ă, Ą, Ǎ, Ȁ, Ȃ, Ȧ, Ạ, Ả, Ấ, Ầ, Ẩ, Ẫ, Ậ, Ắ, Ằ, Ẳ, Ẵ, Ặ

# Missing from standard 26-letter English alphabet would be 3 letters

# Let me look at the NFD decompositions again and see if they match
# the standard xkcd scream cipher combining marks

standard_xkcd = {
    'A': 'A',      # A
    'Ȧ': 'B',      # dot above
    # C: A+cedilla (not in ciphertext)
    # D: A+macron below (not in ciphertext)
    'Á': 'E',      # acute
    # F: A+breve below (not in ciphertext)
    # G: A+double acute (not in ciphertext)
    # H: A+tilde below (not in ciphertext)
    'Ả': 'I',      # hook above
    # J: A+comma above (not in ciphertext)
    'Ạ': 'K',      # dot below
    'Ă': 'L',      # breve
    'Ǎ': 'M',      # caron
    # N: A+circumflex (not in ciphertext - but we have Â? No, Â is not in ciphertext either!)
    # O: A+ring above (not in ciphertext)
    # P: A+inverted breve below (not in ciphertext)
    # Q: A+diaeresis below (not in ciphertext)
    'Ȃ': 'R',      # inverted breve
    # S: A+tilde (not in ciphertext)
    'Ā': 'T',      # macron
    'Ä': 'U',      # diaeresis
    'À': 'V',      # grave
    'Ȁ': 'W',      # double grave
    # X: A+x above (not in ciphertext)
    # Y: A+comma below (not in ciphertext)
    # Z: A+stroke (not in ciphertext)
    # But we have: Ą (A+ogonek) - could be Y (comma below similar to ogonek)
}

# So the standard mapping only gives us 13 characters.
# The remaining 10 are Vietnamese compound chars.

# Maybe the Vietnamese chars encode 2 letters each? Like Ấ = A+circumflex+acute = N+E?
# But some of these compound chars appear frequently...

# Wait, let me check if maybe these compound chars were created by
# normalization/rendering differences. Perhaps the original text uses
# A + combining marks (like the standard scream cipher) but they got
# rendered as precomposed Vietnamese chars?

# Let me check: what does A+U+0302 (circumflex) + U+0301 (acute) look like in NFC?
import unicodedata
nfc = unicodedata.normalize('NFC', 'A\u0302\u0301')
nfd = unicodedata.normalize('NFD', 'A\u0302\u0301')
print(f"A+circumflex+acute: NFC={repr(nfc)} (U+{ord(nfc):04X}), NFD={repr(nfd)}")

# A+U+0306 (breve) + U+0301 (acute)
nfc2 = unicodedata.normalize('NFC', 'A\u0306\u0301')
nfd2 = unicodedata.normalize('NFD', 'A\u0306\u0301')
print(f"A+breve+acute: NFC={repr(nfc2)} (U+{ord(nfc2):04X}), NFD={repr(nfd2)}")

# Hmm interesting! So NFC normalization converts characters like
# A + combining mark into precomposed forms. Let me check if the
# Vietnamese chars in the ciphertext could be NFC-normalized versions
# of standard scream cipher chars.

# For example, standard scream cipher has:
# N = A + U+0302 (circumflex) = Â (precomposed)
# E = A + U+0301 (acute) = Á (precomposed)

# What if the challenge text was created by taking the standard scream cipher
# text and then NFC-normalizing it? If the original had two consecutive
# combining marks on one A, NFC would produce a single Vietnamese char.

# But that doesn't make sense because each A should only have ONE combining mark
# in the standard scream cipher.

# Unless... the challenge creator made a mistake or used a different implementation
# that NFC-normalized the output, and two different A+mark sequences got merged?

# Actually wait - let me look at this from the other direction.
# What if the plaintext has consecutive letters that use combining marks
# that when NFC-normalized produce Vietnamese chars?

# In the standard scream cipher:
# N = Â (A+circumflex)
# E = Á (A+acute)
# So "NE" would be "ÂÁ" in ciphertext - two separate characters
# This NFC normalizes the same way.

# But if someone accidently typed "Â" and then followed it with an acute,
# NFC would produce Ấ (A+circumflex+acute). But that would be a bug.

# Let me just try the approach of treating all the standard matching chars
# with the xkcd mapping and leaving the rest as unknowns, then try to fill
# in using context.

print()

# Let me build the partial mapping
mapping = {
    'A': 'A',   # A
    'Ȧ': 'B',   # dot above
    'Á': 'E',   # acute 
    'Ả': 'I',   # hook above
    'Ạ': 'K',   # dot below
    'Ă': 'L',   # breve
    'Ǎ': 'M',   # caron
    'Ȃ': 'R',   # inverted breve
    'Ā': 'T',   # macron
    'Ä': 'U',   # diaeresis
    'À': 'V',   # grave
    'Ȁ': 'W',   # double grave
    'Ą': 'Y',   # ogonek (similar to combining comma below=Y)
}

# Test decode
decoded = ''.join(mapping.get(c, f'[{ord(c):04X}]') for c in ciphertext)
print("With standard xkcd + guess for Ą=Y:")
print(decoded[:100], "...")
print()

# Let me also try with Ą = something else
# Actually, let me count how many unknown chars we have
unknown = [c for c in ciphertext if c not in mapping]
print(f"Unknown chars (should map to: C, D, F, G, H, J, N, O, P, Q, S, X, Z):")
unknown_set = set(unknown)
print(f"Number of unknown chars: {len(unknown_set)}")
for c in sorted(unknown_set):
    print(f"  {c} U+{ord(c):04X}")


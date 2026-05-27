# Let me try to use the standard scream cipher mapping and see what we get
# Then try to fill in the gaps

ciphertext = "ÁẨĀǍẦĀẶẰẨǍĄẦẤĂẤĂĀȀẨȀẶǍẠẢĄẨÁÀẨĂĂĀȦẨẮĂẤȀȦĀĂẤÀẢẪẨĂẮẴĂĄẤĄẮĄẤẲȀẲAẶẲẮǍĂẨĄẦẤĂĂẦẲẮẪÁẴẨĂẮẢẨǍẨĀĂẠẴẮĄÀĀẠẴẨẠẲẮȦẨĄẦẨĀÁĀẶẦẨĂẨĄĄẤȀȦẮẢẠẲẮǍẶǍĀẶẰẨǍÁẲẤȀȦĄẦẤĂẴẠẦĀȀÁÀẤȦẦĄẴẨĀẪĂẲĀȀȀẲẠẤȀȦĄẦĀȀẰĂĄẲĄẦẨẪẲẲẰĀẪẤẰẨĂĄẦẨẶẦĀǍĀẶĄẨǍĂĀǍẨẮĄAĂẲẤĄĂĀẪĂẲĀẢǍẲẴẪẨÀĄẲẤÁẨȀĄẤAẠĄẦẨẴẠĄẨĂÀĀẠẴẨẪẨĄẮĂẰȀẲÄẤȀĄẦẨȂẲĄẨĂĀȀÁĂẲẪẮĄẤẲȀẴẲĀǍÁĀẴẲẮĄẠẲẮǍẨẬẢẨǍẤẨȀẶẨĀȀẠÄĀẠȀẴǍẦẲÁȀẶÁAÀẨẤĂẠẲẮǍĂẲẪẮĄẤẲȀ"

# Standard xkcd scream cipher mapping (from explainxkcd)
xkcd_map = {
    'A': 'A',      # A
    'Ȧ': 'B',      # A with dot above
    'Ă': 'L',      # A with breve
    'Ǎ': 'M',      # A with caron
    'Á': 'E',      # A with acute
    'À': 'V',      # A with grave
    'Ä': 'U',      # A with diaeresis
    'Ā': 'T',      # A with macron
    'Ả': 'I',      # A with hook above
    'Ạ': 'K',      # A with dot below
    'Ȁ': 'W',      # A with double grave
    'Ȃ': 'R',      # A with inverted breve
}

# Characters in ciphertext not in xkcd map:
# Ą - A with ogonek -> ?? (similar to Y = A+U+0326, but Ą = A+U+0328)
# Ấ - A with circumflex and acute -> ?? (not in xkcd)
# Ầ - A with circumflex and grave -> ??
# Ẩ - A with circumflex and hook above -> ??
# Ẫ - A with circumflex and tilde -> ??
# Ậ - A with circumflex and dot below -> ??
# Ắ - A with breve and acute -> ??
# Ằ - A with breve and grave -> ??
# Ẳ - A with breve and hook above -> ??
# Ẵ - A with breve and tilde -> ??
# Ặ - A with breve and dot below -> ??

# Let's try decoding with just the known chars and see the pattern
decoded = ''
for c in ciphertext:
    if c in xkcd_map:
        decoded += xkcd_map[c]
    else:
        decoded += f'[{ord(c):04X}]'

print("Partial decode with standard xkcd mapping:")
print(decoded)
print()

# Let me try a different approach. Maybe the challenge uses a custom mapping.
# Let me look at the challenge description again - "I stole this cipher from the internets"
# Maybe gizmore used the actual xkcd mapping but with different precomposed chars?

# Let me check what characters the standard scream cipher maps to:
# From xkcd: A, Ȧ, A̧, A̱, Á, A̮, A̋, A̰, Ả, A̓, Ạ, Ă, Ǎ, Â, Å, A̯, A̤, Ȃ, Ã, Ā, Ä, À, Ȁ, A̽, A̦, Ⱥ
# Precomposed forms that exist:
# À, Á, Â, Ã, Ä, Å, Ā, Ă, Ą(ogonek vs cedilla?), Ǎ, Ȁ, Ȃ, Ȧ, Ạ, Ả - these are precomposed
# A̧(U+0041+U+0327), A̱(U+0041+U+0331), A̮(U+0041+U+032E), A̋(U+0041+U+030B), A̰(U+0041+U+0330), 
# A̓(U+0041+U+0313), A̯(U+0041+U+032F), A̤(U+0041+U+0324), A̽(U+0041+U+033D), A̦(U+0041+U+0326), Ⱥ - these have no precomposed form

# So the standard xkcd cipher uses some precomposed characters and some decomposed (A + combining mark)
# The challenge seems to use Vietnamese characters which are NOT in the standard xkcd set!

# OK let me think about this differently. Maybe the challenge creator 
# replaced some characters in the standard xkcd mapping with visually similar 
# Vietnamese characters to confuse people?

# OR maybe the challenge is NOT using xkcd scream cipher at all, but just a regular
# substitution cipher where the glyphs happen to look like A.

# Since it's "simple substitution with an additional problem" and the additional problem
# is "glyphs look alike", let me just solve it as a standard substitution cipher.

# Let me use a more sophisticated approach with an automated solver
# First, let me see if there's a way to find word boundaries

# Check if spaces are represented somehow
# In standard xkcd scream cipher, spaces pass through unchanged
# But the challenge says "punctuation has been removed"

# Maybe the original text had punctuation that was stripped, and the resulting
# text has no spaces either? Or spaces are kept?

# Let me look at the ciphertext for any character that could be a space
# None of the characters look like a space

# Actually, maybe the simplest approach: the challenge expects us to recognize 
# the xkcd scream cipher, use the known mapping for the characters that match,
# and figure out the rest by context.

# But there are 11 Vietnamese compound chars that don't match the xkcd standard!
# These would need to be mapped differently.

# Let me check if any Vietnamese characters map to the standard scream cipher chars
# via NFC normalization

import unicodedata

# Let's see NFC normalization of the Vietnamese chars
viet_chars = ['Ấ', 'Ầ', 'Ẩ', 'Ẫ', 'Ậ', 'Ắ', 'Ằ', 'Ẳ', 'Ẵ', 'Ặ']
for c in viet_chars:
    nfc = unicodedata.normalize('NFC', c)
    nfd = unicodedata.normalize('NFD', c)
    print(f"{c} (U+{ord(c):04X}): NFC={repr(nfc)}, NFD={repr(nfd)}")

print()

# Also check Ą
c = 'Ą'
nfd = unicodedata.normalize('NFD', c)
print(f"{c} (U+{ord(c):04X}): NFD={repr(nfd)}")


#!/usr/bin/env python3

ciphertext = "ÁẨĀǍẦĀẶẰẨǍĄẦẤĂẤĂĀȀẨȀẶǍẠẢĄẨÁÀẨĂĂĀȦẨẮĂẤȀȦĀĂẤÀẢẪẨĂẮẴĂĄẤĄẮĄẤẲȀẲAẶẲẮǍĂẨĄẦẤĂĂẦẲẮẪÁẴẨĂẮẢẨǍẨĀĂẠẴẮĄÀĀẠẴẨẠẲẮȦẨĄẦẨĀÁĀẶẦẨĂẨĄĄẤȀȦẮẢẠẲẮǍẶǍĀẶẰẨǍÁẲẤȀȦĄẦẤĂẴẠẦĀȀÁÀẤȦẦĄẴẨĀẪĂẲĀȀȀẲẠẤȀȦĄẦĀȀẰĂĄẲĄẦẨẪẲẲẰĀẪẤẰẨĂĄẦẨẶẦĀǍĀẶĄẨǍĂĀǍẨẮĄAĂẲẤĄĂĀẪĂẲĀẢǍẲẴẪẨÀĄẲẤÁẨȀĄẤAẠĄẦẨẴẠĄẨĂÀĀẠẴẨẪẨĄẮĂẰȀẲÄẤȀĄẦẨȂẲĄẨĂĀȀÁĂẲẪẮĄẤẲȀẴẲĀǍÁĀẴẲẮĄẠẲẮǍẨẬẢẨǍẤẨȀẶẨĀȀẠÄĀẠÁẢÀÁẪẢẶẴAẦȀĂẤĂẠẲẮǍĂẲẪẮĄẤẲȀ"

# xkcd Scream Cipher mapping (cipher -> plain)
# Based on the explainxkcd table
# Pre-composed characters only
xkcd = {
    'A': 'A',      # U+0041
    'À': 'V',      # U+00C0
    'Á': 'E',      # U+00C1
    'Ä': 'U',      # U+00C4
    'Ā': 'T',      # U+0100
    'Ă': 'L',      # U+0102
    'Ǎ': 'M',      # U+01CD
    'Ȁ': 'W',      # U+0200
    'Ȃ': 'R',      # U+0202
    'Ȧ': 'B',      # U+0226
    'Ạ': 'K',      # U+1EA0
    'Ả': 'I',      # U+1EA2
}

# Let me try: Ą (ogonek) might represent C (cedilla)
xkcd['Ą'] = 'C'  # U+0104 - ogonek looks like cedilla

# For the Vietnamese double-diacritic characters, let me try assigning them
# based on which base diacritic they use and the xkcd mapping for that diacritic

# The 10 Vietnamese chars are based on:
# Â (circumflex) - maps to N in xkcd
# Ă (breve) - maps to L in xkcd
# With tone marks that themselves would be:
# Á (acute) -> E, À (grave) -> V, Ả (hook) -> I, Ã (tilde) -> S, Ạ (dot below) -> K

# Let me try first just the known mappings and see what we get
decoded = ''
for c in ciphertext:
    if c in xkcd:
        decoded += xkcd[c]
    else:
        # Show codepoint
        decoded += f'[{ord(c):04X}]'

print("Direct xkcd mapping (known chars only):")
print(decoded)
print()

# Let me also show the codepoints for unknown chars in order
unknown_seen = set()
for c in ciphertext:
    if c not in xkcd and c not in unknown_seen:
        unknown_seen.add(c)
        print(f"Unknown: U+{ord(c):04X} = '{c}'")

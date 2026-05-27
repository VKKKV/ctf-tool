# Let me encode some common phrases using the standard xkcd scream cipher
# and see if I can find patterns in the ciphertext

xkcd_standard = {
    'A': 'A',
    'B': '\u0226',  # Ȧ
    'C': 'A\u0327',  # A+cedilla
    'D': 'A\u0331',  # A+macron below
    'E': '\u00C1',  # Á
    'F': 'A\u032E',  # A+breve below
    'G': 'A\u030B',  # A+double acute
    'H': 'A\u0330',  # A+tilde below
    'I': '\u1EA2',  # Ả
    'J': 'A\u0313',  # A+comma above
    'K': '\u1EA0',  # Ạ
    'L': '\u0102',  # Ă
    'M': '\u01CD',  # Ǎ
    'N': '\u00C2',  # Â
    'O': '\u00C5',  # Å
    'P': 'A\u032F',  # A+inverted breve below
    'Q': 'A\u0324',  # A+diaeresis below
    'R': '\u0202',  # Ȃ
    'S': '\u00C3',  # Ã
    'T': '\u0100',  # Ā
    'U': '\u00C4',  # Ä
    'V': '\u00C0',  # À
    'W': '\u0200',  # Ȁ
    'X': 'A\u033D',  # A+x above
    'Y': 'A\u0326',  # A+comma below
    'Z': '\u023A',  # Ⱥ
}

def encode_xkcd(text):
    result = ''
    for ch in text.upper():
        if ch in xkcd_standard:
            result += xkcd_standard[ch]
        else:
            result += ch
    return result

# Encode some common phrases
phrases = [
    "HELLO",
    "HI",
    "WELLDONE",
    "CONGRATULATIONS",
    "THE",
    "YOURSOLUTIONIS",
    "PASSWORD",
    "SOLUTION",
    "GOODJOB",
    "THECHALLENGESOLUTIONIS",
]

for phrase in phrases:
    encoded = encode_xkcd(phrase)
    print(f"{phrase:30s} -> {repr(encoded)}")

print()

# Now let me compare with the ciphertext
ciphertext = "ÁẨĀǍẦĀẶẰẨǍĄẦẤĂẤĂĀȀẨȀẶǍẠẢĄẨÁÀẨĂĂĀȦẨẮĂẤȀȦĀĂẤÀẢẪẨĂẮẴĂĄẤĄẮĄẤẲȀẲAẶẲẮǍĂẨĄẦẤĂĂẦẲẮẪÁẴẨĂẮẢẨǍẨĀĂẠẴẮĄÀĀẠẴẨẠẲẮȦẨĄẦẨĀÁĀẶẦẨĂẨĄĄẤȀȦẮẢẠẲẮǍẶǍĀẶẰẨǍÁẲẤȀȦĄẦẤĂẴẠẦĀȀÁÀẤȦẦĄẴẨĀẪĂẲĀȀȀẲẠẤȀȦĄẦĀȀẰĂĄẲĄẦẨẪẲẲẰĀẪẤẰẨĂĄẦẨẶẦĀǍĀẶĄẨǍĂĀǍẨẮĄAĂẲẤĄĂĀẪĂẲĀẢǍẲẴẪẨÀĄẲẤÁẨȀĄẤAẠĄẦẨẴẠĄẨĂÀĀẠẴẨẪẨĄẮĂẰȀẲÄẤȀĄẦẨȂẲĄẨĂĀȀÁĂẲẪẮĄẤẲȀẴẲĀǍÁĀẴẲẮĄẠẲẮǍẨẬẢẨǍẤẨȀẶẨĀȀẠÄĀẠȀẴǍẦẲÁȀẶÁAÀẨẤĂẠẲẮǍĂẲẪẮĄẤẲȀ"

# Check if "THE" (ĄẦẨ) matches
print(f"Does 'THE' appear in ciphertext as Ā? No, T=Ā in xkcd")
print(f"T in xkcd = {repr(xkcd_standard['T'])} (Ā)")
print(f"H in xkcd = A\u0330 (not in ciphertext)")
print(f"E in xkcd = {repr(xkcd_standard['E'])} (Á)")

# So THE would be: Ā + A̰ + Á (in standard xkcd)
# But in the ciphertext, the most common trigram is ĄẦẨ 
# These are different characters!

# The ciphertext uses characters that don't match the standard xkcd mapping!
# For instance:
# The ciphertext has Ą (A+ogonek) but standard xkcd uses Ā (A+macron) for T
# The ciphertext has Ầ (A+circumflex+grave) but standard xkcd uses A̰ (A+tilde below) for H
# The ciphertext has Ẩ (A+circumflex+hook) but standard xkcd uses Á (A+acute) for E

# So the challenge is definitely using a CUSTOM mapping, not the exact xkcd one!

print("\nCiphertext chars vs standard xkcd mapping:")
chars_in_ct = set(ciphertext)
for ct_char in sorted(chars_in_ct):
    nfd = unicodedata.normalize('NFD', ct_char)
    nfd_hex = [hex(ord(x)) for x in nfd]
    print(f"  {ct_char} U+{ord(ct_char):04X}: NFD={nfd_hex}")

import unicodedata

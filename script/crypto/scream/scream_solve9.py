#!/usr/bin/env python3

ciphertext = "ÁẨĀǍẦĀẶẰẨǍĄẦẤĂẤĂĀȀẨȀẶǍẠẢĄẨÁÀẨĂĂĀȦẨẮĂẤȀȦĀĂẤÀẢẪẨĂẮẴĂĄẤĄẮĄẤẲȀẲAẶẲẮǍĂẨĄẦẤĂĂẦẲẮẪÁẴẨĂẮẢẨǍẨĀĂẠẴẮĄÀĀẠẴẨẠẲẮȦẨĄẦẨĀÁĀẶẦẨĂẨĄĄẤȀȦẮẢẠẲẮǍẶǍĀẶẰẨǍÁẲẤȀȦĄẦẤĂẴẠẦĀȀÁÀẤȦẦĄẴẨĀẪĂẲĀȀȀẲẠẤȀȦĄẦĀȀẰĂĄẲĄẦẨẪẲẲẰĀẪẤẰẨĂĄẦẨẶẦĀǍĀẶĄẨǍĂĀǍẨẮĄAĂẲẤĄĂĀẪĂẲĀẢǍẲẴẪẨÀĄẲẤÁẨȀĄẤAẠĄẦẨẴẠĄẨĂÀĀẠẴẨẪẨĄẮĂẰȀẲÄẤȀĄẦẨȂẲĄẨĂĀȀÁĂẲẪẮĄẤẲȀẴẲĀǍÁĀẴẲẮĄẠẲẮǍẨẬẢẨǍẤẨȀẶẨĀȀẠÄĀẠÁẢÀÁẪẢẶẴAẦȀĂẤĂẠẲẮǍĂẲẪẮĄẤẲȀ"

# Let me try using frequency analysis to map the remaining unknown characters.
# Known from xkcd:
known = {
    'A': 'A',
    'À': 'V',
    'Á': 'E',
    'Ä': 'U',
    'Ā': 'T',
    'Ă': 'L',
    'Ǎ': 'M',
    'Ȁ': 'W',
    'Ȃ': 'R',
    'Ȧ': 'B',
    'Ạ': 'K',
    'Ả': 'I',
    'Ą': 'C',  # ogonek ≈ cedilla
}

# The remaining characters and how many times they appear:
# Ẩ: 35, Ẳ: 26, Ấ: 21, Ắ: 17, Ầ: 16, Ẵ: 12, Ẫ: 11, Ặ: 10, Ằ: 6, Ậ: 1
# Wait, let me recalculate

# Let me do a frequency count of the ciphertext directly
freq = {}
for c in ciphertext:
    if c not in freq:
        freq[c] = 0
    freq[c] += 1

print("Ciphertext frequencies:")
for c, count in sorted(freq.items(), key=lambda x: -x[1]):
    known_status = "KNOWN" if c in known else "UNKNOWN"
    print(f"  '{c}' (U+{ord(c):04X}): {count} - {known_status}")

# So the unknown characters by frequency:
# Ẩ: 35, Ẳ: 26, Ấ: 21, Ắ: 17, Ầ: 16, Ẵ: 12, Ẫ: 11, Ặ: 10, Ằ: 6, Ậ: 1

# The remaining letters to assign (A-W minus the 13 known):
# A, V, E, U, T, L, M, W, R, B, K, I, C
# So remaining: D, F, G, H, J, N, O, P, Q, S (10 letters)
# Plus we have 10 unknown chars.

# But wait, we have one more - Ą which we guessed is C.
# That might be wrong. Let me be more careful.

# Let me try: what if the mapping is simply by Unicode codepoint order?
# Let me try ordering the ciphertext chars by Unicode codepoint and mapping
# the first to A, second to B, etc.

# Actually, let me try a different approach entirely.
# Let me look at this as a substitution cipher and use a solver.

# The fact that this is from xkcd 3054 "Scream Cipher" means the mapping
# should follow the xkcd cipher. Let me look at the characters more carefully.

# From the xkcd comic's table, the pre-composed characters used are:
# A (U+0041), Ȧ (U+0226), Á (U+00C1), Ả (U+1EA2), Ạ (U+1EA0), 
# Ă (U+0102), Ǎ (U+01CD), Ȃ (U+0202), Ā (U+0100), Ä (U+00C4), 
# À (U+00C0), Ȁ (U+0200)

# And for C: the xkcd comic uses A̧ (U+0041+U+0327, combining cedilla)
# The challenge uses Ą (U+0104, A with ogonek) which looks similar.

# For the remaining letters D, F, G, H, J, P, Q:
# xkcd uses combining chars: A̱, A̮, A̋, A̰, A̓, A̯, A̤
# No pre-composed forms exist for these.

# For N (Â U+00C2), O (Å U+00C5), S (Ã U+00C3):
# Pre-composed forms exist but are NOT in the ciphertext.
# Instead, the ciphertext has Vietnamese double-diacritic chars.

# The Vietnamese chars in the ciphertext:
# Circumflex group: Ấ(1EA4), Ầ(1EA6), Ẩ(1EA8), Ẫ(1EAA), Ậ(1EAC)
# Breve group: Ắ(1EAE), Ằ(1EB0), Ẳ(1EB2), Ẵ(1EB4), Ặ(1EB6)

# Possible approach: Map the remaining chars based on something.
# Let me try the theory that the Vietnamese chars use their "base" diacritic 
# to determine the letter.

# In the Vietnamese system:
# Â = base letter A with circumflex -> in xkcd, circumflex = N
# Ă = base letter A with breve -> in xkcd, breve = L

# So characters based on Â (circumflex) might substitute for N in xkcd?
# And characters based on Ă (breve) might substitute for L in xkcd?
# But we already have L mapped (Ă -> L).

# Hmm, let me look at the xkcd explainxkcd page notes more carefully.
# For N (Â): "The circumflex peak mirrors the peak at the top left of the N."
# For O (Å): "The symbol contains the letter 'O'."
# For S (Ã): "Tilde looks like a sideways 'S'."

# What if in the WeChall challenge:
# The Vietnamese circumflex group maps to the letters that would use those 
# combining chars? Like Ấ, Ầ, Ẩ, Ẫ, Ậ might map to some of the remaining letters?

# Actually, let me try the simplest possible approach.
# Let me just try ALL possible mappings and see which gives readable text.

# For now, let me use a constraint-based approach.
# I'll iterate: make a guess, decode, see if it looks like English, refine.

# First, let me look at what English words might appear based on the known letters.

print("\n\nTrying to decode with known xkcd mapping + guesses...")

# Let me try assigning the remaining chars based on frequency.
# The most common English letters not yet mapped: N, O, D, H, S, F, G, P, J, Q
# The most frequent UNKNOWN ciphertext chars: Ẩ(35), Ẳ(26), Ấ(21), Ắ(17), Ầ(16)

# Ẩ appears 35 times - most frequent unknown. In English, E is most common,
# but E is already mapped. T is also common but taken. N is next.
# So let me try Ẩ = N (3rd most common English letter)

# Let me just try Ẩ = N first and see what happens
test_map = dict(known)
test_map['Ẩ'] = 'N'  # 35 times, very frequent

decoded = ''.join(test_map.get(c, '?') for c in ciphertext)
print(f"\nWith Ẩ=N:")
# Let me show the first 100 chars
print(decoded[:100])
print()

# Look for "THE" (GOP in our label system) or similar patterns
# With current known mapping + Ẩ=N:
# Let's decode and look for "the" pattern
# The word "the" would be T+H+E in plaintext
# T is Ā, H is unknown, E is Á
# So we'd need to find Ā??Á in the labels where ?? are H and E mapping
# With our labels: Ā (T) + ? (H) + Á (E)
# In the actual ciphertext, "the" pattern would be: Ā?Á 
# Wait, let me search for Ā?Á in the ciphertext directly

# Let me check positions where Ā (T) and Á (E) are separated by one char
for i in range(len(ciphertext)-2):
    if ciphertext[i] == 'Ā' and ciphertext[i+2] == 'Á':
        middle = ciphertext[i+1]
        if middle not in known:
            print(f"  T?E pattern at {i}: '{middle}' (U+{ord(middle):04X}) is potentially 'H'")
# Actually that would be T ? E which could be THE if ? = H

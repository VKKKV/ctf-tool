import unicodedata

ciphertext = "ÁẨĀǍẦĀẶẰẨǍĄẦẤĂẤĂĀȀẨȀẶǍẠẢĄẨÁÀẨĂĂĀȦẨẮĂẤȀȦĀĂẤÀẢẪẨĂẮẴĂĄẤĄẮĄẤẲȀẲAẶẲẮǍĂẨĄẦẤĂĂẦẲẮẪÁẴẨĂẮẢẨǍẨĀĂẠẴẮĄÀĀẠẴẨẠẲẮȦẨĄẦẨĀÁĀẶẦẨĂẨĄĄẤȀȦẮẢẠẲẮǍẶǍĀẶẰẨǍÁẲẤȀȦĄẦẤĂẴẠẦĀȀÁÀẤȦẦĄẴẨĀẪĂẲĀȀȀẲẠẤȀȦĄẦĀȀẰĂĄẲĄẦẨẪẲẲẰĀẪẤẰẨĂĄẦẨẶẦĀǍĀẶĄẨǍĂĀǍẨẮĄAĂẲẤĄĂĀẪĂẲĀẢǍẲẴẪẨÀĄẲẤÁẨȀĄẤAẠĄẦẨẴẠĄẨĂÀĀẠẴẨẪẨĄẮĂẰȀẲÄẤȀĄẦẨȂẲĄẨĂĀȀÁĂẲẪẮĄẤẲȀẴẲĀǍÁĀẴẲẮĄẠẲẮǍẨẬẢẨǍẤẨȀẶẨĀȀẠÄĀẠȀẴǍẦẲÁȀẶÁAÀẨẤĂẠẲẮǍĂẲẪẮĄẤẲȀ"

# Standard xkcd scream cipher mapping (precomposed characters)
# From explainxkcd: A->A, B->Ȧ, E->Á, I->Ả, K->Ạ, L->Ă, M->Ǎ, R->Ȃ, T->Ā, U->Ä, V->À, W->Ȁ
xkcd_standard = {
    'A': 'A',
    'Ȧ': 'B',
    'Á': 'E',
    'Ả': 'I',
    'Ạ': 'K',
    'Ă': 'L',
    'Ǎ': 'M',
    'Ȃ': 'R',
    'Ā': 'T',
    'Ä': 'U',
    'À': 'V',
    'Ȁ': 'W',
}

# Characters in ciphertext not in standard mapping:
# Ą (A+ogonek) - could map to Y (Y=A+comma below, similar)
# Ấ (A+circumflex+acute) - Vietnamese compound
# Ầ (A+circumflex+grave)
# Ẩ (A+circumflex+hook)
# Ẫ (A+circumflex+tilde)
# Ậ (A+circumflex+dot below)
# Ắ (A+breve+acute)
# Ằ (A+breve+grave)
# Ẳ (A+breve+hook)
# Ẵ (A+breve+tilde)
# Ặ (A+breve+dot below)

# Let me try NFD normalization approach
# Decompose each character into base A + combining marks
# Then map each combining mark to a letter using the xkcd mapping
# For characters with multiple combining marks, maybe they encode multiple letters

# The NFD should give us A + combining characters
# Let me build a mapping from combining mark to letter

# Standard xkcd mapping using combining marks:
combining_to_letter = {
    '\u0307': 'B',  # dot above -> Ȧ
    '\u0327': 'C',  # cedilla -> A̧ (not in ciphertext)
    '\u0331': 'D',  # macron below -> A̱
    '\u0301': 'E',  # acute -> Á
    '\u032E': 'F',  # breve below -> A̮
    '\u030B': 'G',  # double acute -> A̋
    '\u0330': 'H',  # tilde below -> A̰
    '\u0309': 'I',  # hook above -> Ả
    '\u0313': 'J',  # comma above -> A̓
    '\u0323': 'K',  # dot below -> Ạ
    '\u0306': 'L',  # breve -> Ă
    '\u030C': 'M',  # caron -> Ǎ
    '\u0302': 'N',  # circumflex -> Â
    '\u030A': 'O',  # ring above -> Å
    '\u032F': 'P',  # inverted breve below -> A̯
    '\u0324': 'Q',  # diaeresis below -> A̤
    '\u0311': 'R',  # inverted breve -> Ȃ
    '\u0303': 'S',  # tilde -> Ã
    '\u0304': 'T',  # macron -> Ā
    '\u0308': 'U',  # diaeresis -> Ä
    '\u0300': 'V',  # grave -> À
    '\u030F': 'W',  # double grave -> Ȁ
    '\u033D': 'X',  # x above -> A̽
    '\u0326': 'Y',  # comma below -> A̦
    '\u0337': 'Z',  # short stroke -> Ⱥ
}

# Try decoding by NFD decomposition
print("Attempting NFD-based decode:")
result = ""
for i, c in enumerate(ciphertext):
    nfd = unicodedata.normalize('NFD', c)
    if nfd[0] == 'A' and len(nfd) == 1:
        # Plain A
        result += 'A'
    elif nfd[0] == 'A':
        # A + combining marks
        marks = nfd[1:]
        letters = []
        for m in marks:
            if m in combining_to_letter:
                letters.append(combining_to_letter[m])
            else:
                letters.append(f'[{hex(ord(m))}]')
        result += ''.join(letters)
    else:
        result += f'?{c}?'

print(result[:200])
print("...")
print()

# Let's also check what each ciphertext char decomposes to
print("Character decomposition:")
unique_chars = sorted(set(ciphertext))
for c in unique_chars:
    nfd = unicodedata.normalize('NFD', c)
    marks_hex = [hex(ord(x)) for x in nfd[1:]]
    letter_map = [combining_to_letter.get(x, '?') for x in nfd[1:]]
    print(f"  {c} U+{ord(c):04X}: A + {marks_hex} -> {''.join(letter_map)}")

#!/usr/bin/env python3

ciphertext = "ÁẨĀǍẦĀẶẰẨǍĄẦẤĂẤĂĀȀẨȀẶǍẠẢĄẨÁÀẨĂĂĀȦẨẮĂẤȀȦĀĂẤÀẢẪẨĂẮẴĂĄẤĄẮĄẤẲȀẲAẶẲẮǍĂẨĄẦẤĂĂẦẲẮẪÁẴẨĂẮẢẨǍẨĀĂẠẴẮĄÀĀẠẴẨẠẲẮȦẨĄẦẨĀÁĀẶẦẨĂẨĄĄẤȀȦẮẢẠẲẮǍẶǍĀẶẰẨǍÁẲẤȀȦĄẦẤĂẴẠẦĀȀÁÀẤȦẦĄẴẨĀẪĂẲĀȀȀẲẠẤȀȦĄẦĀȀẰĂĄẲĄẦẨẪẲẲẰĀẪẤẰẨĂĄẦẨẶẦĀǍĀẶĄẨǍĂĀǍẨẮĄAĂẲẤĄĂĀẪĂẲĀẢǍẲẴẪẨÀĄẲẤÁẨȀĄẤAẠĄẦẨẴẠĄẨĂÀĀẠẴẨẪẨĄẮĂẰȀẲÄẤȀĄẦẨȂẲĄẨĂĀȀÁĂẲẪẮĄẤẲȀẴẲĀǍÁĀẴẲẮĄẠẲẮǍẨẬẢẨǍẤẨȀẶẨĀȀẠÄĀẠÁẢÀÁẪẢẶẴAẦȀĂẤĂẠẲẮǍĂẲẪẮĄẤẲȀ"

unique_chars = sorted(set(ciphertext))
char_to_label = {}
label_to_char = {}
for i, c in enumerate(unique_chars):
    label = chr(ord('A') + i)
    char_to_label[c] = label
    label_to_char[label] = c

labels = ''.join(char_to_label[c] for c in ciphertext)

# Let me try a more systematic approach.
# I'll look for common English words and see if their patterns match.

# First, let me look at the first word. It's likely "Congratulations" or "Hello" or something.

# The text starts with: CPEHOEWTPH
# If this is "CONGRATULATIONS"...
# CONGRATULATIONS = 16 letters
# Let me see: C P E H O E W T P H G O N F N F E I P I W H L M G P C B P F F E K P S F N I K E F N B M Q P F S V F G N G S G N U I U A W U S H F P G O N F F O U S Q C V P F S M P H P E F L V S G B E L V P L U S K P G O P E C E W O P F P G G N I K S M L U S H W H E W T P H C U N I K G O N F V L O E I C B N K O G V P E Q F U E I I U L N I K G O E I T F G U G O P Q U U T E Q N T P F G O P W O E H E W G P H F E H P S G A F U N G F E Q F U E M H U V Q P B G U N C P I G N A L G O P V L G P F B E L V P Q P G S F T I U D N I G O P J U G P F E I C F U Q S G N U I V U E H C E V U S G L U S H P R M P H N P I W P E I L D E L C M B C Q M W V A O I F N F L U S H F U Q S G N U I

# Hmm this is complex. Let me try a different approach.
# Let me look for patterns that might be "the" (THE in English)
# In our labels, "USH" appears 4 times. Could "USH" be "THE"?
# If USH = THE, then U=T, S=H, H=E

# Let me also check "GOP" - 5 times. Could be "AND" 
# If GOP = AND, then G=A, O=N, P=D

# Let me try this combination and see what text we get

mapping = {}  # label -> plaintext letter

# Try USH = THE
mapping['U'] = 'T'
mapping['S'] = 'H'
mapping['H'] = 'E'

# Try GOP = AND
mapping['G'] = 'A'
mapping['O'] = 'N'
mapping['P'] = 'D'

# Let's also look at what "NIK" might be (4 times)
# Could be "ING" - very common suffix
mapping['N'] = 'I'
mapping['I'] = 'N'
mapping['K'] = 'G'

# Let's see what we get
decoded = ''
for c in labels:
    if c in mapping:
        decoded += mapping[c]
    else:
        decoded += '_'

print("With mapping USH=THE, GOP=AND, NIK=ING:")
print(decoded)
print()

# Let me show the original labels with the decoded beneath
print("Original labels:")
print(labels)
print()
print("Decoded (partial):")
print(decoded)

# Let me also check what words we can identify
# Let me look at the decoded text with spaces
print("\n\nDecoded with word boundaries guessed:")
# Print it with a space where we see word boundaries
for i, (l, d) in enumerate(zip(labels, decoded)):
    print(d if d != '_' else l, end='')
print()

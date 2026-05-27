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

# Let me try GOP = THE (most common trigram = most common word)
mapping = {}
mapping['G'] = 'T'  # GOP -> THE
mapping['O'] = 'H'
mapping['P'] = 'E'

# Now let's look at what NIK could be. It appears 4 times.
# With current mapping: N_I_K where O=H, P=E, G=T
# NIK could be "ING" (common suffix)
mapping['N'] = 'I'
mapping['I'] = 'N'
mapping['K'] = 'G'

# "USH" appears 4 times. With current mapping: U_S_H
# U_S_H where S is unknown, H is unknown
# Could be "YOU" or "ARE" or "FOR" or "AND" or "THE" (but the is already mapped)

# Let me first see what we have
decoded = ''
for c in labels:
    if c in mapping:
        decoded += mapping[c]
    else:
        decoded += '_'

print("With GOP=THE, NIK=ING:")
print(decoded)
print()

# Let me look at common words to identify more mappings.
# The text might start with "CONGRATULATIONS"
# Labels start: C P E H O E W T P H G O N F N F E I P I W H L M G P C B P F F E K P S F N I K E F N B M Q P F S V F G N G S G N U I U A W U S H F P G O N F F O U S Q C V P F S M P H P E F L V S G B E L V P L U S K P G O P E C E W O P F P G G N I K S M L U S H W H E W T P H C U N I K G O N F V L O E I C B N K O G V P E Q F U E I I U L N I K G O E I T F G U G O P Q U U T E Q N T P F G O P W O E H E W G P H F E H P S G A F U N G F E Q F U E M H U V Q P B G U N C P I G N A L G O P V L G P F B E L V P Q P G S F T I U D N I G O P J U G P F E I C F U Q S G N U I V U E H C E V U S G L U S H P R M P H N P I W P E I L D E L C M B C Q M W V A O I F N F L U S H F U Q S G N U I

# Let me look at "EWTPH" which appears twice (positions 5 and 124)
# With mapping: G=T, O=H, P=E, N=I, I=N, K=G
# E_W_T_P_H = _W_TEHE
# Hmm, "EWTPH" = E W T P H
# With mapping: E _ _ E _ E (E, W, T, P, H -> E, W, T, E, H)
# If GOP=THE (G=T, O=H, P=E), then EWTPH = E W T E H
# Actually: E=?, W=?, T=?, P=E, H=?
# So EWTPH = ? ? ? E ?

# Let me look at what happens at position 5 and 124
# Position 5-10: EWTPH 
# Position 124-129: EWTPH

# Let me try to see what "the" in context might tell us
# At positions 65-67: "PGO" - this would be "EHT" from our mapping... 
# Wait, PGO = EHT which is "THE" reversed. Interesting.

# Let me look at "FUQSGNUIVUEHCEVUS"
# This appears near the end. Could this contain the password?

# Let me look at the end of the message:
# Last 20 chars: LUSHFUQSGNUI
# With our mapping: _ _ _ _ _ _ _ _ _ _ _ _ 

# Actually, let me try a different approach. Let me search for common words by pattern.

# Let me look at the "A" characters in the ciphertext (plain A).
# Position 59: A (in context: UAW)
# Position 202: A (in context: GAF)
# Position 228: A (in context: CPIGNAL)
# Position 311: A (in context: MWVAO)

# Since there are 4 plain A's, and "A" is a common English word...
# If we think "A" maps to "A" (the letter A), then:
# At position 59: UA W -> ? A W -> context UA was before USHF which we think might be "THE"
# Actually, let me check: "UAW" at position 57-59
# This appears in "GNUIUAWUSHF" 
# With mapping: T I _ _ _ A _ _ T H E
# Not clear.

# Let me try with a fresh approach. Let me just try GOP=AND (if G=A, O=N, P=D)
# instead of GOP=THE.

# Actually, let me just try many possible mappings systematically
# and score them against an English dictionary.

# For now let me just try GOP=AND (A_N_D)
print("\n\nLet me try GOP=AND:")
mapping2 = {
    'G': 'A',
    'O': 'N',
    'P': 'D',
}

# NIK could be "THE" or "ING" or "ION"
# Let me try NIK=ING
mapping2['N'] = 'I'
mapping2['I'] = 'N'
mapping2['K'] = 'G'

decoded2 = ''
for c in labels:
    if c in mapping2:
        decoded2 += mapping2[c]
    else:
        decoded2 += '_'

print(decoded2)

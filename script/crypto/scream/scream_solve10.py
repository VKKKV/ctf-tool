#!/usr/bin/env python3

ciphertext = "ÁẨĀǍẦĀẶẰẨǍĄẦẤĂẤĂĀȀẨȀẶǍẠẢĄẨÁÀẨĂĂĀȦẨẮĂẤȀȦĀĂẤÀẢẪẨĂẮẴĂĄẤĄẮĄẤẲȀẲAẶẲẮǍĂẨĄẦẤĂĂẦẲẮẪÁẴẨĂẮẢẨǍẨĀĂẠẴẮĄÀĀẠẴẨẠẲẮȦẨĄẦẨĀÁĀẶẦẨĂẨĄĄẤȀȦẮẢẠẲẮǍẶǍĀẶẰẨǍÁẲẤȀȦĄẦẤĂẴẠẦĀȀÁÀẤȦẦĄẴẨĀẪĂẲĀȀȀẲẠẤȀȦĄẦĀȀẰĂĄẲĄẦẨẪẲẲẰĀẪẤẰẨĂĄẦẨẶẦĀǍĀẶĄẨǍĂĀǍẨẮĄAĂẲẤĄĂĀẪĂẲĀẢǍẲẴẪẨÀĄẲẤÁẨȀĄẤAẠĄẦẨẴẠĄẨĂÀĀẠẴẨẪẨĄẮĂẰȀẲÄẤȀĄẦẨȂẲĄẨĂĀȀÁĂẲẪẮĄẤẲȀẴẲĀǍÁĀẴẲẮĄẠẲẮǍẨẬẢẨǍẤẨȀẶẨĀȀẠÄĀẠÁẢÀÁẪẢẶẴAẦȀĂẤĂẠẲẮǍĂẲẪẮĄẤẲȀ"

# Let me build a dictionary for looking up T?E patterns (could be "THE")
# T = Ā, E = Á

print("Searching for T?E pattern (possible 'THE'):")
for i in range(len(ciphertext)-2):
    if ciphertext[i] == 'Ā' and ciphertext[i+2] == 'Á':
        middle = ciphertext[i+1]
        print(f"  pos {i}: '{middle}' (U+{ord(middle):04X}) - context: ...{ciphertext[max(0,i-3):i+6]}...")

print("\nSearching for T?E pattern with known middle:")
for i in range(len(ciphertext)-2):
    if ciphertext[i] == 'Ā' and ciphertext[i+2] == 'Á':
        middle = ciphertext[i+1]
        print(f"  pos {i}: '{middle}' (U+{ord(middle):04X})")

# Also look for "A?A" pattern (maybe "ANA" or "ATA")
print("\nSearching for A?A pattern:")
for i in range(len(ciphertext)-2):
    if ciphertext[i] == 'A' and ciphertext[i+2] == 'A':
        middle = ciphertext[i+1]
        print(f"  pos {i}: '{middle}' (U+{ord(middle):04X})")

# Look for "C?C" pattern if Ą=C
print("\nSearching for C?C pattern (Ą?Ą):")
for i in range(len(ciphertext)-2):
    if ciphertext[i] == 'Ą' and ciphertext[i+2] == 'Ą':
        middle = ciphertext[i+1]
        print(f"  pos {i}: '{middle}' (U+{ord(middle):04X})")

# Look for "L?L" pattern (Ă?Ă):
print("\nSearching for L?L pattern (Ă?Ă):")
for i in range(len(ciphertext)-2):
    if ciphertext[i] == 'Ă' and ciphertext[i+2] == 'Ă':
        middle = ciphertext[i+1]
        print(f"  pos {i}: '{middle}' (U+{ord(middle):04X})")

# Let me look for "TH?" pattern (T+H+? where T=Ā, H=?)
print("\nSearching for TH? pattern (Ā + candidate H + ?):")
# H is unknown but let me try each candidate
for i in range(len(ciphertext)-2):
    if ciphertext[i] == 'Ā':
        second = ciphertext[i+1]
        third = ciphertext[i+2]
        print(f"  pos {i}: TH? = Ā{second}{third}")

ciphertext = "ÁẨĀǍẦĀẶẰẨǍĄẦẤĂẤĂĀȀẨȀẶǍẠẢĄẨÁÀẨĂĂĀȦẨẮĂẤȀȦĀĂẤÀẢẪẨĂẮẴĂĄẤĄẮĄẤẲȀẲAẶẲẮǍĂẨĄẦẤĂĂẦẲẮẪÁẴẨĂẮẢẨǍẨĀĂẠẴẮĄÀĀẠẴẨẠẲẮȦẨĄẦẨĀÁĀẶẦẨĂẨĄĄẤȀȦẮẢẠẲẮǍẶǍĀẶẰẨǍÁẲẤȀȦĄẦẤĂẴẠẦĀȀÁÀẤȦẦĄẴẨĀẪĂẲĀȀȀẲẠẤȀȦĄẦĀȀẰĂĄẲĄẦẨẪẲẲẰĀẪẤẰẨĂĄẦẨẶẦĀǍĀẶĄẨǍĂĀǍẨẮĄAĂẲẤĄĂĀẪĂẲĀẢǍẲẴẪẨÀĄẲẤÁẨȀĄẤAẠĄẦẨẴẠĄẨĂÀĀẠẴẨẪẨĄẮĂẰȀẲÄẤȀĄẦẨȂẲĄẨĂĀȀÁĂẲẪẮĄẤẲȀẴẲĀǍÁĀẴẲẮĄẠẲẮǍẨẬẢẨǍẤẨȀẶẨĀȀẠÄĀẠȀẴǍẦẲÁȀẶÁAÀẨẤĂẠẲẮǍĂẲẪẮĄẤẲȀ"

# Check a few characters to see if they are single code points or combining sequences
print("First 10 character analysis:")
for i, c in enumerate(ciphertext[:10]):
    cp = ord(c)
    if cp >= 0x0300 and cp <= 0x036F:
        print(f"  [{i}] U+{cp:04X} - COMBINING mark: {unicodedata.name(c, 'UNKNOWN')}")
    elif cp >= 0x1DC0 and cp <= 0x1DFF:
        print(f"  [{i}] U+{cp:04X} - Combining mark: {unicodedata.name(c, 'UNKNOWN')}")
    else:
        print(f"  [{i}] U+{cp:04X} ({c}) - {unicodedata.name(c, 'UNKNOWN')}")

print()
print("Are all characters single code points?")
for i, c in enumerate(ciphertext):
    if len(c) != 1:
        print(f"  WARNING: Character at {i} is not a single code point!")
        
# Check if there are any combining characters in the string
import unicodedata
has_combining = False
for i, c in enumerate(ciphertext):
    if unicodedata.combining(c):
        print(f"  Combining char at {i}: U+{ord(c):04X}")
        has_combining = True
if not has_combining:
    print("  No combining characters found - all are precomposed single code points")
    
print()
# Let's also check the NFC and NFD of the first few Vietnamese chars
viet_samples = ['Ấ', 'Ầ', 'Ẩ', 'Ẫ', 'Ậ', 'Ắ', 'Ằ', 'Ẳ', 'Ẵ', 'Ặ']
for c in viet_samples:
    nfd = unicodedata.normalize('NFD', c)
    nfc = unicodedata.normalize('NFC', c)
    print(f"{c} (U+{ord(c):04X}): NFD={[f'U+{ord(x):04X}' for x in nfd]}, NFC={[f'U+{ord(x):04X}' for x in nfc]}")

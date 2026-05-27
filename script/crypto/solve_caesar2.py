import sys

# Hex ciphertext from the page
hex_str = """
14 3C 3C 31 20 37 3C 2F 79 20 46 3C 42 20 40 3C
39 43 32 31 20 3C 3B 32 20 3A 3C 3F 32 20 30 35
2E 39 39 32 3B 34 32 20 36 3B 20 46 3C 42 3F 20
37 3C 42 3F 3B 32 46 7B 20 21 35 36 40 20 3C 3B
32 20 44 2E 40 20 33 2E 36 3F 39 46 20 32 2E 40
46 20 41 3C 20 30 3F 2E 30 38 7B 20 24 2E 40 3B
74 41 20 36 41 0C 20 7E 7F 05 20 38 32 46 40 20
36 40 20 2E 20 3E 42 36 41 32 20 40 3A 2E 39 39
20 38 32 46 40 3D 2E 30 32 79 20 40 3C 20 36 41
20 40 35 3C 42 39 31 3B 74 41 20 35 2E 43 32 20
41 2E 38 32 3B 20 46 3C 42 20 41 3C 3C 20 39 3C
3B 34 20 41 3C 20 31 32 30 3F 46 3D 41 20 41 35
36 40 20 3A 32 40 40 2E 34 32 7B 20 24 32 39 39
20 31 3C 3B 32 79 20 46 3C 42 3F 20 40 3C 39 42
41 36 3C 3B 20 36 40 20 3A 3A 33 31 3A 35 3B 2F
2F 32 2E 33 7B
"""

# Parse hex values
hex_vals = hex_str.strip().split()
cipher_bytes = [int(h, 16) for h in hex_vals]
print(f"Number of bytes: {len(cipher_bytes)}")
print(f"Raw bytes: {bytes(cipher_bytes)}")
print()

# Try all 128 shifts
for shift in range(128):
    decoded = []
    for b in cipher_bytes:
        decoded.append((b - shift) % 128)
    
    # Convert to string, replacing non-printable
    result = ''.join(chr(d) if 32 <= d <= 126 else f'[{d}]' for d in decoded)
    
    # Check if it looks like English
    # Count common English words/patterns
    text_lower = result.lower()
    if 'the ' in text_lower or 'and ' in text_lower or 'that ' in text_lower or 'this ' in text_lower:
        print(f"--- Shift {shift} ---")
        print(result)
        print()

# Also print the raw byte interpretation
print("\n=== All shifts printable slice ===")
for shift in range(128):
    decoded = [(b - shift) % 128 for b in cipher_bytes]
    printable = ''.join(chr(d) if 32 <= d <= 126 else '.' for d in decoded)
    if any(word in printable.lower() for word in ['the', 'and', 'you', 'for', 'are', 'but', 'not', 'have']):
        print(f"Shift {shift:3d}: {printable}")

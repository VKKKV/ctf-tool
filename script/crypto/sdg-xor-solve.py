#!/usr/bin/env python3

# System key extracted via Known-Plaintext Attack
key_hex = "0e0f1011121314151617fffefdfcfbfa0e0f1011121314151617fffefdfcfbfa"

# TODO: Replace this with the actual encrypted prescription code you need to solve
target_ciphertext = "683e2726762270237323ccc9cbc9cace366b7420237120772627ce9acb9d9d99"

# Convert hex to bytes
key_bytes = bytes.fromhex(key_hex)
target_bytes = bytes.fromhex(target_ciphertext)

# XOR decryption (repeating the key if the ciphertext is longer than 16 bytes)
decrypted_bytes = bytes(
    c ^ key_bytes[i % len(key_bytes)] for i, c in enumerate(target_bytes)
)

print(
    f"Decrypted Plaintext (ASCII): {decrypted_bytes.decode('utf-8', errors='ignore')}"
)
print(f"Decrypted Plaintext (Hex): {decrypted_bytes.hex()}")

import base64

# The tampered token (line 108) - only one that decodes to pure binary
ct = base64.b32decode("YX2THEVPQ4LNRIMFCHIKFUCBRL2IGF6567KEFW7Q2AK5XIUEJXI7FUCE33VQ====")
print(f"Ciphertext ({len(ct)} bytes): {ct.hex()}")

# The flag format starts with "SDG{" - use as known plaintext to derive the 4-byte XOR key
known = b"SDG{"
key = bytes([ct[i] ^ known[i] for i in range(4)])
print(f"Derived XOR key: {key.hex()}")

# Decrypt with repeating 4-byte key
plaintext = bytes([ct[i] ^ key[i % 4] for i in range(len(ct))])
print(f"Decrypted: {plaintext.decode()}")


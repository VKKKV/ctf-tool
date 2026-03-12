#!/usr/bin/env python3

def main():

    # 1. Generate 16 8-bit characters from assembly operations
    unlock_chars = [
        0x4B ^ 0x0C,  # mov al, 4Bh ; xor al, 0Ch
        0x53 ^ 0x06,  # mov al, 53h ; xor al, 6
        0x58 - 0x01,  # mov al, 58h ; sub al, 1
        0x62 - 0x29,  # mov al, 62h ; sub al, 29h
        0x68 ^ 0x23,  # mov al, 68h ; xor al, 23h
        0x4B ^ 0x00,  # mov al, 4Bh ; xor al, 0
        0x62 - 0x1E,  # mov al, 62h ; sub al, 1Eh
        0x4D - 0x0B,  # mov al, 4Dh ; sub al, 0Bh
        0x45 ^ 0x0D,  # mov al, 45h ; xor al, 0Dh
        0x10 ^ 0x28,  # mov al, 10h ; xor al, 28h
        0x58 ^ 0x1D,  # mov al, 58h ; xor al, 1Dh
        0x7A ^ 0x28,  # mov al, 7Ah ; xor al, 28h
        0x65 - 0x13,  # mov al, 65h ; sub al, 13h
        0x33 ^ 0x07,  # mov al, 33h ; xor al, 7
        0x25 ^ 0x15,  # mov al, 25h ; xor al, 15h
        0x4C + 0x0C,  # mov al, 4Ch ; add al, 0Ch
    ]

    unlock_code = "".join(chr(c) for c in unlock_chars)
    print(f"[+] Unlock Code: {unlock_code}")

    # 2. Encrypted Payload (32 bytes) from Hex Dump
    payload_hex = "77 21 67 30 60 35 0c 0c 78 79 2e 2e 20 72 70 75 29 2b 00 5c 21 70 62 63 65 60 07 0d 06 02 3b 3b"
    encrypted_bytes = bytes.fromhex(payload_hex)

    # 3. Core Decryption Pipeline
    # Each unlock_char is used to decrypt two payload bytes (index i // 2)
    decrypted_chars = [
        chr(byte ^ unlock_chars[i // 2])
        for i, byte in enumerate(encrypted_bytes)
    ]

    flag_core = "".join(decrypted_chars)
    print(f"247CTF{{{flag_core}}}")


if __name__ == "__main__":
    main()

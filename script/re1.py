#!/usr/bin/env python3

def main():

    unlock_code = "GUW9KKDBH8ERR40X"

    # 2. 从 Hex Dump 的 0x01B1 处提取的加密 Payload (32 bytes)
    payload_hex = "77 21 67 30 60 35 0c 0c 78 79 2e 2e 20 72 70 75 29 2b 00 5c 21 70 62 63 65 60 07 0d 06 02 3b 3b"

    # 将 Hex 字符串转换为整数列表
    encrypted_bytes = [int(b, 16) for b in payload_hex.split()]

    decrypted_chars = []

    # 3. 核心解密流水线 (The Pipeline)
    for i, byte in enumerate(encrypted_bytes):
        # 0 // 2 => 0, 1 // 2 => 0, 2 // 2 => 1, 3 // 2 => 1
        key_char = unlock_code[i // 2]

        # 将密文字节与密码字符的 ASCII 值进行 XOR (异或) 运算
        decrypted_byte = byte ^ ord(key_char)

        decrypted_chars.append(bytes.fromhex(f"{decrypted_byte:02x}").decode())

    flag_core = "".join(decrypted_chars)
    print(f"247CTF{{{flag_core}}}")


if __name__ == "__main__":
    main()

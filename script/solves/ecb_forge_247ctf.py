import binascii

import requests

BASE_URL = "https://2c5a74f7cc3f1fdf.247ctf.com"


def solve():

    part1_plain = b"impossible_flag_"

    payload1 = binascii.hexlify(part1_plain).decode()
    r1 = requests.get(f"{BASE_URL}/encrypt?user={payload1}")

    cipher_part1 = r1.text[:32]
    print(f"[*] Block 1 Cipher: {cipher_part1}")

    padding_len = 16 - (20 % 16)
    part2_plain = b"user" + bytes([padding_len] * padding_len)
    payload2 = binascii.hexlify(part2_plain).decode()
    r2 = requests.get(f"{BASE_URL}/encrypt?user={payload2}")

    cipher_part2 = r2.text[:32]
    print(f"[*] Block 2 Cipher: {cipher_part2}")

    final_token = cipher_part1 + cipher_part2
    print(f"[*] Forged Token: {final_token}")

    r_flag = requests.get(f"{BASE_URL}/get_flag?user={final_token}")
    print(f"\n---> FLAG: {r_flag.text}")


if __name__ == "__main__":
    solve()

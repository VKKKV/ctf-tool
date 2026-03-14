import string

import requests
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
from Crypto.Util.Padding import pad
from pwn import *
from pwn import b64d, b64e, context, enhex, log, process, remote, unhex, xor

# 16 bytes 128 bits a time
# PKCS#7 default pad()

context.log_level = "info"

charset = string.printable.strip()

p = process(["/challenge/run"], stdin=process.PTY, stdout=process.PTY)

log.info("Start")

result = b""

block_size = 16


def send_part_of_flag(data):
    p.recvuntil(b"Data? ")
    p.sendline(enhex(data))

    p.recvuntil(b"Ciphertext: ")
    ct = unhex(p.recvline().strip())
    return ct


for i in range(1, 58):
    block_idx = (i - 1) // block_size

    pad_len = (block_size - i) % block_size

    padding = b"A" * pad_len

    ct = send_part_of_flag(padding)

    target_block = ct[block_idx * 16 : (block_idx + 1) * 16]

    for c in charset:
        c = c.encode()
        ct2 = send_part_of_flag(padding + result + c)
        guess_block = ct2[block_idx * 16 : (block_idx + 1) * 16]
        if guess_block == target_block:
            log.success(f"Found: {c} at {i}")
            result = result + c
            break

print(result)

p.interactive()

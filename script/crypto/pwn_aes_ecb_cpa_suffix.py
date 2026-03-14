import string

import requests
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
from Crypto.Util.Padding import pad
from pwn import *
from pwn import b64d, b64e, context, enhex, log, process, remote, unhex, xor

# PKCS#7 default pad()

context.log_level = "info"

charset = string.printable.strip()

p = process(["/challenge/run"], stdin=process.PTY, stdout=process.PTY)

log.info("Start")

result = ""

# start

def cpa(data):
    p.recvuntil(b"Choice? ")
    p.sendline(b"1")

    p.recvuntil(b"Data? ")
    p.sendline(data)

    p.recvuntil(b"Result: ")
    ct = unhex(p.recvline().strip())
    return ct


def get_part_of_flag(length):
    p.recvuntil(b"Choice? ")
    p.sendline(b"2")

    p.recvuntil(b"Length? ")
    p.sendline(str(length))

    p.recvuntil(b"Result: ")
    ct = unhex(p.recvline().strip())
    return ct


for i in range(1, 58):
    pt = get_part_of_flag(i)
    for c in charset:
        data = cpa(c + result)
        if data == pt:
            log.success(f"Found: {c} at {i}")
            result = c + result
            break

print(result)

p.interactive()

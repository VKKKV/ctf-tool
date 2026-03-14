import string

from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
from Crypto.Util.Padding import pad
from pwn import *
from pwn import context, enhex, log, process, unhex, xor

# block cipher
# 16 bytes 128 bits a time

# ECB mode

# known plaintext attack

# chosen ciphertext attack

context.log_level = "info"

charset = string.printable.strip()

p = process(["/challenge/run"], stdin=process.PTY, stdout=process.PTY)

log.info("Start")


def cpa(data):
    p.recvuntil(b"Choice? ")
    p.sendline("1")

    p.recvuntil(b"Data? ")
    p.sendline(data)

    p.recvuntil(b"Result: ")
    ct = unhex(p.recvline().strip())
    return ct


def get_part_of_flag(index, length=1):
    p.recvuntil(b"Choice? ")
    p.sendline("2")

    p.recvuntil(b"Index? ")
    p.sendline(str(index))

    p.recvuntil(b"Length? ")
    p.sendline(str(length))

    p.recvuntil(b"Result: ")
    ct = unhex(p.recvline().strip())
    return ct


result = ""

for i in range(0, 57):
    pt = get_part_of_flag(i)
    for c in charset:
        data = cpa(c)
        if data == pt:
            log.success(f"Found: {c} at {i}")
            result += c
            break

print(result)

p.interactive()

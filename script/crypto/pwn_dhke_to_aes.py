from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
from Crypto.Random.random import getrandbits
from Crypto.Util.Padding import pad, unpad
from pwn import *
from pwn import context, enhex, log, process, unhex, xor

pro = process(["/challenge/run"], stdin=process.PTY, stdout=process.PTY)

log.info("START")

pro.recvuntil(b"p = ")
p = int(pro.recvline().strip(), 16)

pro.recvuntil(b"g = ")
g = int(pro.recvline().strip(), 16)

pro.recvuntil(b"A = ")
A = int(pro.recvline().strip(), 16)

B = p
pro.recvuntil(b"B? ")
pro.sendline(f"{B:#x}")

s = 0
key = s.to_bytes(256, "little")[:16]

pro.recvuntil(b"Flag Ciphertext (hex): ")
ciphertext = unhex(pro.readline().strip())

cipher = AES.new(key=key, mode=AES.MODE_CBC)

flag = cipher.decrypt(ciphertext)

print(flag)

pro.interactive()

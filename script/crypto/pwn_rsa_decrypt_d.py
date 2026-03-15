from Crypto.Cipher import AES
from Crypto.PublicKey import RSA
from Crypto.Random import get_random_bytes
from Crypto.Random.random import getrandbits
from Crypto.Util.Padding import pad, unpad
from pwn import *
from pwn import context, enhex, log, process, unhex, xor

pro = process(["/challenge/run"], stdin=process.PTY, stdout=process.PTY)
log.info("START")
pro.recvuntil(b"(public)  n = ")
n = int(pro.recvline().strip(), 16)

pro.recvuntil(b"(public)  e = ")
e = int(pro.recvline().strip(), 16)

pro.recvuntil(b"(private) d = ")
d = int(pro.recvline().strip(), 16)

pro.recvuntil(b"Flag Ciphertext (hex): ")
ciphertext = unhex(pro.readline().strip())

flag = pow(int.from_bytes(ciphertext, "little"), d, n).to_bytes(256, "little")

print(flag)

pro.interactive()

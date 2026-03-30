"""RSA: generate own keypair, sign server challenge, decrypt secret."""
import base64
import json
import pathlib
import random
import string
import sys
import textwrap

from Crypto.Cipher import AES
from Crypto.Hash.SHA256 import SHA256Hash
from Crypto.PublicKey import RSA
from Crypto.Random import get_random_bytes
from Crypto.Random.random import getrandbits, randrange
from Crypto.Util.Padding import pad, unpad
from Crypto.Util.strxor import strxor
from pwn import *
from pwn import context, enhex, log, process, unhex, xor, b64d

pro = process(["/challenge/run"], stdin=process.PTY, stdout=process.PTY)
log.info("START")

key = RSA.generate(1024)

e = key.e
d = key.d
n = key.n
pro.recvuntil(b"e: ")
pro.sendline(hex(e)[2:].encode())

pro.recvuntil(b"n: ")
pro.sendline(hex(n)[2:].encode())

pro.recvuntil(b"challenge: ")
challenge = int(pro.recvline().strip(), 16)

ciphertext = pow(challenge, d, n)

pro.recvuntil(b"response: ")
# 把整数转成十六进制字符串，切掉 0x，再编码成 bytes 流
pro.sendline(hex(ciphertext)[2:].encode())

pro.recvuntil(b"secret ciphertext (b64): ")
b = b64d(pro.recvline().strip())

flag = int.from_bytes(b, "little")

print(pow(flag, d, n).to_bytes(256, "little"))

pro.interactive()

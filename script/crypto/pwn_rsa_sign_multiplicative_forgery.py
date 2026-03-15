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
from pwn import b64d, b64e, context, enhex, log, process, unhex, xor

log.info("START")

n = int(open("/challenge/key-n").read(), 16)
e = int(open("/challenge/key-e").read(), 16)

# The target integer representation of b"flag" (little endian)
# 0x67616c66 = 1734437990
target_int = int.from_bytes(b"flag", "little")

# Factor the integer into two parts to bypass the "flag" substring filter
m1 = 2
m2 = target_int // 2

# Convert factors back to bytes
command1 = m1.to_bytes(1, "little")
command2 = m2.to_bytes(4, "little")

c1 = b64e(command1).encode()
c2 = b64e(command2).encode()

# Fetch signature 1
p1 = process(["/challenge/dispatcher", c1])
p1.recvuntil(b"Signed command (b64): ")
signature1 = int.from_bytes(b64d(p1.recvline().strip()), "little")
p1.close()

# Fetch signature 2
p2 = process(["/challenge/dispatcher", c2])
p2.recvuntil(b"Signed command (b64): ")
signature2 = int.from_bytes(b64d(p2.recvline().strip()), "little")
p2.close()

# Homomorphic Multiplication to forge the final signature
signature = pow(signature1 * signature2, 1, n).to_bytes(256, "little")

# Profit
p3 = process(["/challenge/worker", b64e(signature)])
p3.interactive()

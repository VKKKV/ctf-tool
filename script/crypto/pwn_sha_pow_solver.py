import base64
import hashlib
import itertools
import json
import os
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

p = process(["/challenge/run"], stdin=process.PTY, stdout=process.PTY)

prefix_length = 6
difficulty = 2

p.recvuntil(b"challenge (b64): ")
challenge = b64d(p.recvline().strip())

# 使用 itertools.count 替代手动 while 循环累加，减少 Python 字节码层面的开销
for count in itertools.count():
    # better count.to_bytes(4, "little")
    if SHA256Hash(challenge + count.to_bytes(256, "big")).digest()[:difficulty] == (
        b"\0" * difficulty
    ):
        break

    count += 1
    if count % 1000000 == 0:
        log.info(f"Tried {count} combinations...")

p.recvuntil(b"response (b64): ")
p.sendline(b64e(count.to_bytes(256, "big")))

p.interactive()

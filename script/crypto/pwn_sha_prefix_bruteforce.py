import base64
import hashlib
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

p.recvuntil(b"flag_hash[:prefix_length]=")
collision = p.recvline().strip().replace(b"'", b"").decode()

prefix_length = 6
count = 0

while True:
    flag = str(count).encode()
    flag_hash = hashlib.sha256(flag).hexdigest()

    if flag_hash[:prefix_length] == collision:
        break

    count += 1
    if count % 1000000 == 0:
        log.info(f"Tried {count} combinations...")


p.sendlineafter(b"Colliding input? ", flag.hex().encode())
p.interactive()

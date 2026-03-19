"""TLS cert forgery: sign user cert with leaked root key d, decrypt secret."""
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

user_key = RSA.generate(1024)

p = process(["/challenge/run"], stdin=process.PTY, stdout=process.PTY)

p.recvuntil(b"root key d: ")
d = int(p.recvline().strip(), 16)

p.recvuntil(b"root certificate (b64): ")
cert = b64d(p.recvline().strip())

p.recvuntil(b"root certificate signature (b64): ")
cert_sig = b64d(p.recvline().strip())


root_cert_dict = json.loads(cert)
root_n = root_cert_dict["key"]["n"]

user_cert_dict = {
    "name": "user",
    "key": {
        "e": user_key.e,
        "n": user_key.n,
    },
    "signer": "root",
}

user_cert_data = json.dumps(user_cert_dict).encode()
user_cert_hash = SHA256Hash(user_cert_data).digest()

user_cert_signature = pow(int.from_bytes(user_cert_hash, "little"), d, root_n).to_bytes(
    256, "little"
)

p.recvuntil(b"user certificate (b64): ")
p.sendline(b64e(user_cert_data))

p.recvuntil(b"user certificate signature (b64): ")
p.sendline(b64e(user_cert_signature).encode())

p.recvuntil(b"secret ciphertext (b64): ")
ciphertext = b64d(p.recvline().strip())

flag_int = pow(int.from_bytes(ciphertext, "little"), user_key.d, user_key.n)

flag = flag_int.to_bytes(256, "little").replace(b"\x00", b"")
log.success(f"Flag recovered: {flag.decode('utf-8')}")

p.interactive()

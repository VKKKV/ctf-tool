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
from Crypto.Hash import SHA256
from Crypto.Hash.SHA256 import SHA256Hash
from Crypto.PublicKey import RSA
from Crypto.Random import get_random_bytes
from Crypto.Random.random import getrandbits, randrange
from Crypto.Util.Padding import pad, unpad
from Crypto.Util.strxor import strxor
from pwn import *
from pwn import b64d, b64e, context, enhex, log, process, unhex, xor

p = process(["/challenge/run"])

log.info("START")

# 1. 提取 DH 参数和 Root 信息
p.recvuntil(b"p: ")
dh_p = int(p.recvline().strip(), 16)
p.recvuntil(b"g: ")
dh_g = int(p.recvline().strip(), 16)

p.recvuntil(b"root key d: ")
root_d = int(p.recvline().strip(), 16)

p.recvuntil(b"root certificate (b64): ")
root_cert_b64 = p.recvline().strip()
root_cert = json.loads(b64d(root_cert_b64).decode())
root_n = root_cert["key"]["n"]

# 跳过 root cert signature 输出
p.recvuntil(b"root certificate signature (b64): ")
p.recvline()

# 2. 获取 Client 信息
p.recvuntil(b"name: ")
client_name = p.recvline().strip().decode()
log.info(f"Target connection name: {client_name}")

p.recvuntil(b"A: ")
client_A = int(p.recvline().strip(), 16)

# 3. Diffie-Hellman Key Exchange
log.info("Initiating DH Key Exchange...")
b_priv = random.getrandbits(2048)
server_B = pow(dh_g, b_priv, dh_p)

# 发送我们的 Public Key B
p.recvuntil(b"B: ")
p.sendline(hex(server_B)[2:].encode())

# 计算 Shared Secret 并派生 AES Key
shared_secret = pow(client_A, b_priv, dh_p)
aes_key = SHA256.new(shared_secret.to_bytes(256, "little")).digest()[:16]

# 初始化 AES-CBC Cipher (Encryptor)
cipher_encrypt = AES.new(key=aes_key, mode=AES.MODE_CBC, iv=b"\0" * 16)


def encrypt_and_b64(data: bytes) -> bytes:
    padded_data = pad(data, 16)
    encrypted = cipher_encrypt.encrypt(padded_data)
    return b64e(encrypted).encode()


# 4. 伪造 User Certificate
log.info("Forging user certificate and signatures...")
user_key = RSA.generate(1024)

user_cert_dict = {
    "name": client_name,  # 必须匹配 Client 请求的名字
    "key": {
        "e": user_key.e,
        "n": user_key.n,
    },
    "signer": "root",
}

user_cert_data = json.dumps(user_cert_dict).encode()
user_cert_hash = SHA256.new(user_cert_data).digest()

# 用泄漏的 root 私钥签名 User Cert
user_cert_sig = pow(int.from_bytes(user_cert_hash, "little"), root_d, root_n).to_bytes(
    256, "little"
)

# 5. 生成 User Handshake Signature
signature_payload = (
    client_name.encode().ljust(256, b"\0")
    + client_A.to_bytes(256, "little")
    + server_B.to_bytes(256, "little")
)
user_sig_hash = SHA256.new(signature_payload).digest()

# 用我们刚才生成的 user 私钥签名 handshake payload
user_signature = pow(
    int.from_bytes(user_sig_hash, "little"), user_key.d, user_key.n
).to_bytes(256, "little")

# 6. 发送加密的握手数据
log.info("Sending encrypted payload via secure channel...")
p.recvuntil(b"user certificate (b64): ")
p.sendline(encrypt_and_b64(user_cert_data))

p.recvuntil(b"user certificate signature (b64): ")
p.sendline(encrypt_and_b64(user_cert_sig))

p.recvuntil(b"user signature (b64): ")
p.sendline(encrypt_and_b64(user_signature))

# 7. 解密 Flag
p.recvuntil(b"secret ciphertext (b64): ")
encrypted_flag = b64d(p.recvline().strip())

# 初始化一个新的 AES Cipher 用于 Decrypt (因为 AES.CBC 是有状态的，或者用同一个重置 IV，但新开一个更稳)
cipher_decrypt = AES.new(key=aes_key, mode=AES.MODE_CBC, iv=b"\0" * 16)
flag = unpad(cipher_decrypt.decrypt(encrypted_flag), 16).decode()

log.success(f"{flag}")

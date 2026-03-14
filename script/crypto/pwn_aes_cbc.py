from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
from Crypto.Util.Padding import pad
from pwn import *
from pwn import log, process, xor, context

# CBC mode
# cipher block chaining
# IV Initialization Vector

context.log_level = "info"

p = process(["/challenge/run"], stdin=process.PTY, stdout=process.PTY)

log.info("Start")

p.recvuntil(b"AES Key (hex): ")
key_hex = p.recvline().strip()
key = bytes.fromhex(key_hex.decode())


p.recvuntil(b"Flag Ciphertext (hex): ")
ciphertext_hex = p.recvline().strip()
ciphertext = bytes.fromhex(ciphertext_hex.decode())

cipher = AES.new(key=key, mode=AES.MODE_CBC)
plaintext = cipher.decrypt(ciphertext)

print(f"Flag Plaintext (hex): {plaintext}")

p.interactive()

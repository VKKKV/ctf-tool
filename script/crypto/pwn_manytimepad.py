from pwn import *
from pwn import log, process, xor

context.log_level = "info"

p = process(["/challenge/run"], stdin=process.PTY, stdout=process.PTY)

log.info("Start")
p.recvuntil(b"Flag Ciphertext (hex): ")
cipher_hex = p.recvline().strip()
cipher = bytes.fromhex(cipher_hex.decode())


plaintext = b"A" * len(cipher)

p.recvuntil(b"Plaintext (hex): ")
p.sendline(plaintext.hex())

p.recvuntil(b"Ciphertext (hex): ")
ciphertext_hex = p.recvline().strip()
ciphertext = bytes.fromhex(ciphertext_hex.decode())

key = xor(plaintext, ciphertext)

flag = xor(cipher, key)

print(flag)

p.interactive()

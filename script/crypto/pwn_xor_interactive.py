from pwn import *
from pwn import xor, log, process

p = process("/challenge/run")


for i in range(10):
    log.info(f"正在处理第 {i} 关挑战...")

    # 丢弃无用的行，精准定位我们需要的十六进制数据
    p.recvuntil(b"The key: ")
    key_hex = p.recvline().strip().decode()
    key = int(key_hex, 16)

    p.recvuntil(b"Encrypted secret: ")
    cipher_hex = p.recvline().strip().decode()
    cipher = int(cipher_hex, 16)

    result = key ^ cipher

    p.sendline(hex(result).encode())
    log.success(f"Key: {hex(key)} ^ Cipher: {hex(cipher)} => Result: {hex(result)}")

# 拿下 Flag
p.interactive()

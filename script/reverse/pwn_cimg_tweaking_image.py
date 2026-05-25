"""cIMG exploit: fix corrupted flag.cimg header/pixels to recover flag."""
import struct

from pwn import *
from pwn import ELF, log, process

def fix_image():
    img_path = "/challenge/flag.cimg"
    binary_path = "/challenge/cimg"

    try:
        with open(img_path, "rb") as f:
            broken_img = f.read()
    except FileNotFoundError:
        log.error(f"Cannot find {img_path}. Are you in the right environment?")
        return

    # 1. 解析损坏的 Header
    header_format = "<4sHBBI"
    header_size = struct.calcsize(header_format)

    magic, version, width, height, num_directives = struct.unpack(
        header_format, broken_img[:header_size]
    )

    # 2. 动态计算真实的 Height
    real_height = num_directives // width

    log.info("--- Image Header Analysis ---")
    log.info(f"Magic: {magic}")
    log.info(f"Version: {version}")
    log.info(f"Width: {width}")
    log.warning(f"Fake Height from file: {height}")
    log.success(f"Calculated Real Height: {num_directives} / {width} = {real_height}")

    # 3. 重新打包 Header
    fixed_header = struct.pack(
        header_format, magic, version, width, real_height, num_directives
    )

    # 4. 逐个修复 Directives
    fixed_directives = bytearray()
    directive_size = 10
    expected_opcode = 2
    fixed_opcode = 52965

    offset = header_size
    for i in range(num_directives):
        chunk = broken_img[offset : offset + directive_size]
        if len(chunk) < directive_size:
            break

        opcode, x, y, w, h, r, g, b, char = struct.unpack("<HBBBBBBBB", chunk)

        if opcode == expected_opcode:
            new_chunk = struct.pack(
                "<HBBBBBBBB", fixed_opcode, x, y, w, h, r, g, b, char
            )
            fixed_directives += new_chunk
        else:
            fixed_directives += chunk

        offset += directive_size

    # 5. 组装修复后的镜像
    fixed_img = fixed_header + fixed_directives

    fixed_path = "fixed_flag.cimg"
    with open(fixed_path, "wb") as f:
        f.write(fixed_img)

    p = process([binary_path, fixed_path], stdin=process.PTY, stdout=process.PTY)

    print(p.recvall().decode(errors="ignore"))


if __name__ == "__main__":
    fix_image()

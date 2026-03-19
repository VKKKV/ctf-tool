"""cIMG exploit: parse C source for pixel data, build matching cIMG payload."""
import re
import struct

from pwn import *
from pwn import ELF, ROP, context, log, process, remote


def build_payload():
    # 1. 直接读取目标 C 源码文件
    try:
        with open("/challenge/cimg.c", "r") as f:
            src = f.read()
    except FileNotFoundError:
        return

    # 2. 使用正则提取 desired_output 字符串
    match = re.search(r'char desired_output\[\] = "(.*?)";', src, re.DOTALL)
    if not match:
        return

    raw_c_str = match.group(1)

    # 3. 解除 C 语言的字符串转义 (\x1b -> 真实 ESC 字节, \\ -> \)
    decoded_bytes = bytes(raw_c_str, "utf-8").decode("unicode_escape").encode("latin1")

    # 去除末尾的 C 语言 null terminator (\x00)
    if decoded_bytes.endswith(b"\x00"):
        decoded_bytes = decoded_bytes[:-1]

    # 4. 计算总像素数 (每个终端像素刚好 24 字节)
    # \x1b[38;2;RRR;GGG;BBBmc\x1b[0m
    PIXEL_LEN = 24
    num_pixels = len(decoded_bytes) // PIXEL_LEN

    # 5. 因式分解，找出合法的 width 和 height (都在 0~255 之间)
    width, height = 0, 0
    for w in range(1, 256):
        if num_pixels % w == 0:
            h = num_pixels // w
            if h <= 255:
                width, height = w, h
                break  # 找到第一组满足条件的尺寸

    if width == 0:
        log.error("Could not factorize num_pixels into valid uint8_t bounds.")
        return

    log.info(f"Calculated valid constraints: Width = {width}, Height = {height}")

    # 6. 构造无填充的 8 Bytes Header (<4sHBB)
    magic = b"cIMG"
    version = 2
    file_header = struct.pack("<4sHBB", magic, version, width, height)

    # 7. 提取每个像素的 R, G, B, ASCII 构建数据段
    pixel_data = bytearray()
    for i in range(num_pixels):
        chunk = decoded_bytes[i * PIXEL_LEN : (i + 1) * PIXEL_LEN]

        # 精确内存对齐切片:
        # chunk[7:10] = RRR
        # chunk[11:14] = GGG
        # chunk[15:18] = BBB
        # chunk[19] = ASCII 字符字节
        r = int(chunk[7:10])
        g = int(chunk[11:14])
        b = int(chunk[15:18])
        char_byte = chunk[19]

        pixel_data += struct.pack("<BBBB", r, g, b, char_byte)

    # 8. 组装 Payload 并写入文件
    payload = file_header + pixel_data
    file_name = "payload.cimg"
    with open(file_name, "wb") as f:
        f.write(payload)

    log.success(f"Payload generated: {len(payload)} bytes.")

    # 9. 运行二进制并拿 Flag
    p = process(["/challenge/cimg", file_name], stdin=process.PTY, stdout=process.PTY)
    print(p.recvall().decode(errors="ignore"))


if __name__ == "__main__":
    build_payload()

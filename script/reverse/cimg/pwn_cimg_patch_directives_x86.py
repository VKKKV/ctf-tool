"""cIMG exploit: patch x86 directives using pixel frequency analysis."""
import struct
from collections import Counter

from pwn import *
from pwn import ELF, ROP, context, log, process, remote


def extract_pixels_from_elf(binary_path, num_pixels):
    elf = ELF(binary_path, checksec=False)
    try:
        addr = elf.symbols["desired_output"]
    except:
        addr = 0x404020

    raw = elf.read(addr, num_pixels * 24)
    pixels = []
    for i in range(num_pixels):
        chunk = raw[i * 24 : (i + 1) * 24]
        try:
            r = int(chunk[7:10])
            g = int(chunk[11:14])
            b = int(chunk[15:18])
            c = chunk[19]
            pixels.append((r, g, b, c))
        except:
            pass
    return pixels


def build_payload():
    binary_path = "/challenge/cimg"
    num_pixels = 1314
    width = 73
    height = 18

    pixels = extract_pixels_from_elf(binary_path, num_pixels)
    if len(pixels) != num_pixels:
        log.error("Failed to extract full image from binary.")
        return

    # 1. 寻找主导背景色
    color_counts = Counter(pixels)
    bg_pixel = color_counts.most_common(1)[0][0]
    log.info(f"Dominant background pixel detected: {bg_pixel}")

    # 2. 贪心二维矩形合并算法
    directives_payload = bytearray()
    directive_count = 0
    visited = set()

    # 扫描全局 Framebuffer
    for y in range(height):
        for x in range(width):
            # 如果是需要绘制的前景像素，且未被合并过
            if pixels[y * width + x] != bg_pixel and (x, y) not in visited:
                # a. 横向贪心寻找最大宽度
                w = 0
                while (
                    x + w < width
                    and pixels[y * width + x + w] != bg_pixel
                    and (x + w, y) not in visited
                ):
                    w += 1

                # b. 纵向贪心寻找最大高度 (整行必须完全匹配该宽度且未访问)
                h = 1
                while y + h < height:
                    row_valid = True
                    for i in range(w):
                        if (
                            pixels[(y + h) * width + x + i] == bg_pixel
                            or (x + i, y + h) in visited
                        ):
                            row_valid = False
                            break
                    if row_valid:
                        h += 1
                    else:
                        break

                # c. 标记该矩形区域内的所有像素为已访问
                for dy in range(h):
                    for dx in range(w):
                        visited.add((x + dx, y + dy))

                # d. 构造 45626 区块写入指令 (仅花费 6 Bytes 的 Overhead)
                directives_payload += struct.pack("<H", 45626)
                directives_payload += struct.pack("<BBBB", x, y, w, h)

                # e. 填入该矩形的真实像素数据
                for dy in range(h):
                    for dx in range(w):
                        p = pixels[(y + dy) * width + x + dx]
                        directives_payload += struct.pack(
                            "<BBBB", p[0], p[1], p[2], p[3]
                        )

                directive_count += 1

    log.info(f"Greedy algorithm optimized image into {directive_count} solid blocks.")
    total_size = len(directives_payload) + 12

    if total_size > 1340:
        log.error(f"Bandwidth limit exceeded! Current size: {total_size} bytes.")
        return

    magic = b"cIMG"
    version = 3
    remaining_directives = 1
    file_header = struct.pack(
        "<4sHBBI", magic, version, width, height, remaining_directives
    )

    file_header = struct.pack("<4sHBBI", magic, version, width, height, directive_count)

    # 4. 组装并运行
    payload = file_header + directives_payload
    file_name = "payload.cimg"
    with open(file_name, "wb") as f:
        f.write(payload)

    log.success(f"Payload generated: {len(payload)} bytes.")
    p = process([binary_path, file_name], stdin=process.PTY, stdout=process.PTY)
    print(p.recvall().decode(errors="ignore"))


if __name__ == "__main__":
    build_payload()

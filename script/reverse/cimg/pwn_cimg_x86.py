"""cIMG exploit: craft x86 pixel payload from ELF desired_output."""
import struct

from pwn import *
from pwn import ELF, ROP, context, log, process, remote


def build_payload():
    binary_path = "/challenge/cimg"
    try:
        elf = ELF(binary_path, checksec=False)
    except Exception as e:
        log.error(f"Failed to load ELF: {e}")
        return

    # 2. 我们通过 radare2 分析已知 desired_output 的地址是 0x404020
    # 从汇编 cmp r14d, 0x1e4 得知，总共 484 个像素
    desired_output_addr = 0x404020
    num_pixels = 0x1E4  # 484
    pixel_len = 24
    total_bytes = num_pixels * pixel_len

    log.info(
        f"Extracting {total_bytes} bytes from address {hex(desired_output_addr)}..."
    )

    # 3. 从 ELF 文件中读取这些字节
    try:
        raw_ansi_data = elf.read(desired_output_addr, total_bytes)
    except Exception as e:
        log.error(f"Failed to read from ELF memory: {e}")
        return

    # 4. 提取颜色和字符数据 (<BBBB)
    pixel_data = bytearray()
    for i in range(num_pixels):
        chunk = raw_ansi_data[i * pixel_len : (i + 1) * pixel_len]

        # 典型的 chunk: b'\x1b[38;2;255;255;255m.\x1b[0m'
        # 索引提取: R (7:10), G (11:14), B (15:18), ASCII (19)
        try:
            r = int(chunk[7:10])
            g = int(chunk[11:14])
            b = int(chunk[15:18])
            char_byte = chunk[19]

            pixel_data += struct.pack("<BBBB", r, g, b, char_byte)
        except ValueError as e:
            log.error(f"Failed to parse chunk at index {i}: {chunk}. Error: {e}")
            return

    # 5. 尺寸断言：484 的最佳分解是 22 x 22
    width = 22
    height = 22
    assert width * height == num_pixels, "Dimension logic error!"

    # 6. 打包 Header (<4sHBB)
    magic = b"cIMG"
    version = 2
    file_header = struct.pack("<4sHBB", magic, version, width, height)

    # 7. 组装并保存 Payload
    payload = file_header + pixel_data
    file_name = "payload.cimg"
    with open(file_name, "wb") as f:
        f.write(payload)

    log.success(f"Payload generated: {len(payload)} bytes.")

    # 8. 直接运行目标拿到 Flag
    p = process([binary_path, file_name], stdin=process.PTY, stdout=process.PTY)
    print(p.recvall().decode(errors="ignore"))


if __name__ == "__main__":
    build_payload()

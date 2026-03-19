"""cIMG exploit: extract desired pixels from ELF, generate x86 directive payload."""
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
    try:
        desired_output_addr = elf.symbols["desired_output"]
        log.info(f"Resolved 'desired_output' symbol at: {hex(desired_output_addr)}")
    except KeyError:
        desired_output_addr = 0x404020  # Fallback 地址
        log.warning("Symbol not found, using fallback address.")

    # search from radare2
    num_pixels = 1314
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

    # factor num_pixels
    width = 73
    height = 18
    assert width * height == num_pixels, "Dimension logic error!"

    # I -> 4 bytes
    # B -> 1 byte
    # H -> 2 bytes
    # Q -> 8 bytes
    magic = b"cIMG"
    version = 3
    remaining_directives = 1
    file_header = struct.pack(
        "<4sHBBI", magic, version, width, height, remaining_directives
    )

    # 5. 构造 Directive Code (<H)

    # compacted code
    directive_code = 0x2174

    # normal code
    # directive_code = 0xb23a

    directive_header = struct.pack("<H", directive_code)

    # 7. 组装并保存 Payload
    payload = file_header + directive_header + pixel_data

    file_name = "payload.cimg"
    with open(file_name, "wb") as f:
        f.write(payload)

    log.success(f"Payload generated: {len(payload)} bytes.")

    # 8. 直接运行目标拿到 Flag
    p = process([binary_path, file_name], stdin=process.PTY, stdout=process.PTY)
    print(p.recvall().decode(errors="ignore"))


if __name__ == "__main__":
    build_payload()

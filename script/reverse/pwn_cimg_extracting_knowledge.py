"""cIMG parser: dump flag.cimg header and pixel data to extract hidden flag."""
import struct
import sys


def parse_and_dump_flag():
    img_path = "/challenge/flag.cimg"
    try:
        with open(img_path, "rb") as f:
            data = f.read()
    except FileNotFoundError:
        print(f"[!] Cannot find {img_path}.")
        return

    # 1. 解析 Header
    header_format = "<4sHBBI"
    header_size = struct.calcsize(header_format)
    magic, version, width, height, num_directives = struct.unpack(
        header_format, data[:header_size]
    )

    if magic != b"cIMG":
        print("[!] Invalid magic number.")
        return

    print(f"[*] Parsed Header: {num_directives} directives found.")

    offset = header_size
    sprites = {}
    flag_sequence = []

    # 2. 遍历所有的 Directives，像解析 ELF 节区一样解析它
    for _ in range(num_directives):
        opcode = struct.unpack("<H", data[offset : offset + 2])[0]
        offset += 2

        if opcode == 3:
            # Handle 3: 注册 Sprite
            sp_id, sp_w, sp_h = struct.unpack("<BBB", data[offset : offset + 3])
            offset += 3

            # 读取 Figlet 原始字符数据
            raw_sprite = data[offset : offset + sp_w * sp_h]
            offset += sp_w * sp_h

            # 还原 2D 文本结构
            art = ""
            for i in range(sp_h):
                line = raw_sprite[i * sp_w : (i + 1) * sp_w]
                art += line.decode(errors="ignore") + "\n"
            sprites[sp_id] = art

        elif opcode == 4:
            # Handle 4: 渲染 Sprite
            # 我们不需要管它在屏幕的哪里渲染 (x,y)，只需要记录它渲染了哪个 ID
            sp_id, r, g, b, x, y = struct.unpack("<BBBBBB", data[offset : offset + 6])
            offset += 6
            flag_sequence.append(sp_id)

    print("[*] Data extraction complete.\n")
    print("=" * 60)

    # 3. 按调用顺序打印出 Flag 对应的 Figlet 字符
    for sp_id in flag_sequence:
        if sp_id in sprites:
            print(sprites[sp_id])
            print("-" * 60)
        else:
            print(f"[!] Warning: Missing dependency for sprite ID {sp_id}")


if __name__ == "__main__":
    parse_and_dump_flag()

#!/usr/bin/env python3
import struct
import sys


def main():
    # ---------------------------------------------------------
    # 1. 构造文件头 (Header) - 总计 12 Bytes
    # ---------------------------------------------------------
    # Magic   : "cIMG" -> 小端序存储为 0x474d4963
    # Version : 必须是 4 (汇编中 cmp word [var_ch], 4)
    # Width   : 随便给个 32
    # Height  : 随便给个 32
    # Directs : 我们准备注入 3 条指令
    magic = b"cIMG"
    version = 4
    width = 32
    height = 32
    num_directives = 3

    # 格式化: 4s(字符串), H(无符号短整型), B(无符号字符), B(无符号字符), I(无符号整型)
    header = struct.pack("<4sHBBI", magic, version, width, height, num_directives)
    payload = bytearray(header)

    # ---------------------------------------------------------
    # 2. 注入指令 1: load_sprite_raw (指令码: 3)
    # ---------------------------------------------------------
    # handle_3 逻辑:
    # 读 1 byte 拿到 sprite_id (var_dh)
    # 读 1 byte 拿到 sp_width  (var_eh)
    # 读 1 byte 拿到 sp_height (var_fh)
    # 读取 sp_width * sp_height 个字节的像素数据 (校验须 <= 0x5e 即 '^')
    sprite_id = 0
    sp_w = 2
    sp_h = 2
    # 像素数据使用 'A' (0x41)，满足 <= 0x5e 的合法性检查
    pixel_data = b"AAAA"

    payload += struct.pack("<H", 3)  # Directive code
    payload += struct.pack("<BBB", sprite_id, sp_w, sp_h)
    payload += pixel_data

    # ---------------------------------------------------------
    # 3. 注入指令 2: render_sprite (指令码: 4)
    # ---------------------------------------------------------
    # handle_4 逻辑:
    # 读取 9 bytes: sprite_id, x, y 以及其他渲染参数
    payload += struct.pack("<H", 4)  # Directive code

    # 为了演示，我们把精灵渲染在坐标 (5, 5)，其余参数填 0
    # byte 0: sprite_id (0)
    # byte 1: pos_x (5)
    # byte 2: pos_y (5)
    # byte 3-8: 其他属性 (padding/layer/etc.)
    render_params = struct.pack("<BBBBBBBBB", 0, 5, 5, 0, 0, 0, 0, 0, 0)
    payload += render_params

    # ---------------------------------------------------------
    # 4. 注入指令 3: clear_and_display (指令码: 6)
    # ---------------------------------------------------------
    # handle_6 逻辑:
    # 读取 1 byte 清屏标志，然后调用 sym.display
    payload += struct.pack("<H", 6)  # Directive code
    payload += struct.pack("<B", 1)  # Clear flag = 1

    # 输出到文件
    filename = "exploit.cimg"
    with open(filename, "wb") as f:
        f.write(payload)

    print(f"[*] Payload 已生成: {filename}")


if __name__ == "__main__":
    main()

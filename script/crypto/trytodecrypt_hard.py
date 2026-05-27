#!/usr/bin/env python3
"""trytodecrypt hard solver — 密钥嵌入密文结构，无需 oracle

用法:
  echo '密文' | python trytodecrypt_hard.py <text_id>

Text 13: 首字节为 key，后续每字节减 key
Text 14: 前 3 字节为旋转 key，后续每字节减对应 key
Text 15: 前 6 hex 为 3 子密钥，data - key[i%3] 得字符偏移查表
Text 16: 4-hex 一组(2偏移+2编码)，编码减偏移
Text 17: 前半 key 后半数据，key - 数据
Text 18: 同 Text 17，结果反转
"""

import sys

C = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ-_.,;:?! "

# char -> 字符专用偏移量 (paulfrisby 工作文件 + 推算的大写字母)
CHAR_OFF = {
    'a': 0x27, 'b': 0x0b, 'c': 0x41, 'd': 0x45, 'e': 0x0e,
    'f': 0x10, 'g': 0x11, 'h': 0x05, 'i': 0x2f, 'j': 0x1c,
    'k': 0x16, 'l': 0x18, 'm': 0x04, 'n': 0x35, 'o': 0x3e,
    'p': 0x37, 'q': 0x1d, 'r': 0x1f, 's': 0x15, 't': 0x21,
    'u': 0x1a, 'v': 0x23, 'w': 0x00, 'x': 0x0c, 'y': 0x3b,
    'z': 0x30, '.': 0x03, ' ': 0x12, 'A': 0x1e, 'B': 0x13,
}
# 反转: 偏移 -> char
OFF_CHAR = {v: k for k, v in CHAR_OFF.items()}


def decode_text13(ct):
    """首字节为全局 key"""
    key = int(ct[:2], 16)
    data = [int(ct[i:i+2], 16) for i in range(2, len(ct), 2)]
    return "".join(C[b - key] for b in data)


def decode_text14(ct):
    """前 3 字节为旋转 key"""
    keys = [int(ct[i:i+2], 16) for i in range(0, 6, 2)]
    data = [int(ct[i:i+2], 16) for i in range(6, len(ct), 2)]
    return "".join(C[data[i] - keys[i % 3]] for i in range(len(data)))


def decode_text15(ct):
    """前 6 hex 为 3 子密钥, data - key[i%3] 得偏移查表"""
    keys = [int(ct[i:i+2], 16) for i in range(0, 6, 2)]
    data = [int(ct[i:i+2], 16) for i in range(6, len(ct), 2)]
    plain = ""
    for i, d in enumerate(data):
        off = d - keys[i % 3]
        plain += OFF_CHAR.get(off, "?")
    return plain


def decode_text16(ct):
    """4-hex 一组 (2偏移 + 2编码)"""
    pt = ""
    for i in range(0, len(ct), 4):
        off = int(ct[i:i+2], 16)
        enc = int(ct[i+2:i+4], 16)
        cp = enc - off
        pt += C[cp] if 0 <= cp < len(C) else "?"
    return pt


def decode_text17(ct, reverse=False):
    """前半 key 后半数据, key - 数据"""
    half = len(ct) // 2
    keys = [int(ct[i:i+2], 16) for i in range(0, half, 2)]
    data = [int(ct[i:i+2], 16) for i in range(half, len(ct), 2)]
    pt = "".join(C[keys[i] - data[i]] for i in range(len(data)))
    return pt[::-1] if reverse else pt


def decode_text18(ct):
    """同 Text 17 但结果反转"""
    return decode_text17(ct, reverse=True)


DECODERS = {
    13: decode_text13,
    14: decode_text14,
    15: decode_text15,
    16: decode_text16,
    17: decode_text17,
    18: decode_text18,
}


def main():
    if len(sys.argv) < 2:
        print(f"用法: {sys.argv[0]} <text_id (13-18)>")
        sys.exit(1)

    text_id = int(sys.argv[1])
    ct = sys.stdin.read().strip() if not sys.stdin.isatty() else input("密文: ").strip()

    if text_id not in DECODERS:
        print(f"不支持 text_id={text_id}")
        sys.exit(1)

    print(DECODERS[text_id](ct))


if __name__ == "__main__":
    main()

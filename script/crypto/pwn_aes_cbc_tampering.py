from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
from Crypto.Util.Padding import pad
from pwn import *
from pwn import context, enhex, log, process, unhex, xor

# CBC mode
# cipher block chaining
# IV Initialization Vector
# cbc byte flipping

p1 = process(["/challenge/worker"], stdin=process.PTY, stdout=process.PTY)
p2 = process(["/challenge/dispatcher"], stdin=process.PTY, stdout=process.PTY)

s1 = pad(b"sleep", 16)
s2 = pad(b"flag!", 16)
s2 = pad(b"flag", 16)

log.info("Start")
p2.recvuntil(b"TASK: ")
ct = unhex(p2.recvline().strip())

iv, ct = ct[:16], ct[16:]

iv = xor(xor(iv, s1), s2)

ct = enhex(iv + ct)

p1.sendline(f"TASK: {ct}")

p1.interactive()

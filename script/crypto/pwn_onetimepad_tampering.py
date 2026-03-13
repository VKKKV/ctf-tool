from pwn import *
from pwn import log, process, xor

context.log_level = "info"

# 核心技巧：使用 process.PTY 完美伪装成真实终端，绕过 isatty() 检查
p1 = process(["/challenge/worker"], stdin=process.PTY, stdout=process.PTY)
p2 = process(["/challenge/dispatcher"], stdin=process.PTY, stdout=process.PTY)

s1 = b"sleep"
s2 = b"flag!"


log.info("Start")
p2.recvuntil(b"TASK: ")
cipher_hex = p2.recvline().strip()
cipher = bytes.fromhex(cipher_hex.decode())

key = xor(cipher, s1)

a = xor(key, s2).hex()

p1.sendline(f"TASK: {a}")

p1.interactive()


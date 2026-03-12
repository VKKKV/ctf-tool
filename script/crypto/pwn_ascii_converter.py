import os
import pty
import subprocess

# TODO

from pwn import *
from pwn import log, process, xor

# 创建一个伪终端对
master, slave = pty.openpty()

# 启动挑战程序，并将它的 stdin/stdout/stderr 全部绑定到 slave PTY 上
p = subprocess.Popen(
    ["/challenge/run"],
    stdin=slave,
    stdout=slave,
    stderr=slave,
    text=True,
    close_fds=True,
)

def read_until(suffix):
        buf = ""
        while not buf.endswith(suffix):
            char = os.read(master, 1).decode()
            if not char: break
            buf += char
        return buf

# if not sys.stdin.isatty():
#     print("You must interact with me directly. No scripting this!")
#     sys.exit(1)
#
# for n in range(1, 10):
#     print(f"Challenge number {n}...")
#     pt_chr, ct_chr = random.sample(
#         string.digits + string.ascii_letters + string.punctuation,
#         2
#     )
#     key = ord(pt_chr) ^ ord(ct_chr)
#
#     print(f"- Encrypted Character: {ct_chr}")
#     print(f"- XOR Key: {key:#04x}")
#     answer = input("- Decrypted Character? ").strip()
#     if answer != pt_chr:
#         print("Incorrect!")
#         sys.exit(1)
#
#     print("Correct! Moving on.")
#
# print("You have mastered XORing ASCII! Your flag:")
# print(open("/flag").read())


for i in range(10):
    log.info(f"正在处理第 {i} 关挑战...")

    read_until(b"The key: ")
    key = read_until.strip().decode()

    p.recvuntil(b"Encrypted secret: ")
    cipher = p.recvline().strip().decode()

    result = xor(key, cipher).encode()

    p.sendline(hex(result))
    log.success(f"Key: {hex(key)} ^ Cipher: {hex(cipher)} => Result: {hex(result)}")

# 拿下 Flag
p.interactive()

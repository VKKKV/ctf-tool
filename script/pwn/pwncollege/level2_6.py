from pwn import *


def print_lines(io):
    info("Printing io received lines")
    while True:
        try:
            line = io.recvline()
            success(line.decode())
        except EOFError:
            break


# Set architecture, os and log level
context(arch="amd64", os="linux", log_level="info")

# Load the ELF file and execute it as a new process.
challenge_path = "/challenge/pwntools-tutorials-level2.6"

p = process(challenge_path)

# In this level you need to craft assembly code to complete the following operations:
# * rax = the sum from 1 to rcx

# 1. 准备计算 (rcx + 1)，我们先把 rcx 复制到 rax
# 2. rax = rcx + 1
# 3. 乘法: CPU 会自动计算 rax * rcx，并将低 64-bit 结果存入 rax，高位存入 rdx
# 此时 rax 里就是 n * (n + 1) 的结果
# 4. 除以 2：真正的黑客永远用逻辑右移 (shr) 来代替笨重的 div 指令
p.sendafter(
    "Please give me your assembly in bytes",
    asm("""
    mov rax, rcx
    inc rax
    mul rcx
    shr rax, 1
    """),
)

print_lines(p)

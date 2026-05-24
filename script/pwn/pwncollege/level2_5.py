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
challenge_path = "/challenge/pwntools-tutorials-level2.5"

p = process(challenge_path)

# In this level you need to craft assembly code to complete the following operations:
# * the top value of the stack = abs(the top value of the stack)

p.sendafter(
    "Please give me your assembly in bytes",
    asm("""
    pop rax
    neg rax
    push rax
    """),
)

print_lines(p)

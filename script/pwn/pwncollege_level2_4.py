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
challenge_path = "/challenge/pwntools-tutorials-level2.4"

p = process(challenge_path)

# Send the payload after the string "(up to 0x1000 bytes): \n" is found.
# In this level you need to craft assembly code to complete the following operations:
# * the top value of the stack = the top value of the stack - rbx
# Tips: perfer push and pop instructions, other than directly [esp] dereference

p.sendafter(
    "Please give me your assembly in bytes",
    asm("""
    pop rax
    sub rax, rbx
    push rax
    """),
)

print_lines(p)

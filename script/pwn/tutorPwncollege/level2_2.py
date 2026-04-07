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
challenge_path = "/challenge/pwntools-tutorials-level2.2"

p = process(challenge_path)

# Send the payload after the string "(up to 0x1000 bytes): \n" is found.
p.sendafter(
    "Please give me your assembly in bytes",
    asm("""
    xor rdx, rdx
    div rbx
    mov rax, rdx
    add rax, rcx
    sub rax, rsi
    """),
)

print_lines(p)

from pwn import *

# Set architecture, os and log level
context(arch="amd64", os="linux", log_level="info")

# Load the ELF file and execute it as a new process.
challenge_path = "/challenge/pwntools-tutorials-level1.0"
p = process(challenge_path)

payload = p32(0xdeadbeef)
# Send the payload after the string ":)\n###\n" is found.
p.sendlineafter(":)\n###\n", payload)

# Receive flag from the process
flag = p.recvline()
print(f"flag is: {flag}")

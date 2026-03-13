from pwn import *
from pwn import log, process, xor

context.log_level = "info"

# 核心技巧：使用 process.PTY 完美伪装成真实终端，绕过 isatty() 检查
p = process(["/challenge/run"], stdin=process.PTY, stdout=process.PTY)

log.info("start")

p.recvuntil(b"One-Time Pad Key (hex): ")
ct_hex_str = p.recvline().strip()
ct_str = bytes.fromhex(ct_hex_str.decode())

# 2. 解析 XOR Key
p.recvuntil(b"Flag Ciphertext (hex): ")
key_hex_str = p.recvline().strip()
key_str = bytes.fromhex(key_hex_str.decode())

pt_str = xor(ct_str, key_str).decode()

log.success(f"密文: {ct_hex_str}, Key: {key_hex_str} => 明文: {pt_str}")

# 拿下 Flag 并保持交互
p.interactive()

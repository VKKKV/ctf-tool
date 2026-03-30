"""XOR single-char ASCII decryption challenge solver."""
from pwn import *
from pwn import log, process, xor

context.log_level = "info"

# 核心技巧：使用 process.PTY 完美伪装成真实终端，绕过 isatty() 检查
p = process(["/challenge/run"], stdin=process.PTY, stdout=process.PTY)

for i in range(1, 10):
    log.info(f"正在破解第 {i} 关...")

    p.recvuntil(b"- Encrypted Character: ")
    ct_chr = p.recvline().strip().decode()

    # 2. 解析 XOR Key
    p.recvuntil(b"- XOR Key: ")
    key_str = p.recvline().strip().decode()
    key = int(key_str, 16)  # 把 0x 开头的字符串转为整数

    # 3. 等待输入提示符
    p.recvuntil(b"- Decrypted Character? ")

    # 4. 核心运算：计算明文。将密文字符转 ASCII -> 与 Key 异或 -> 转回字符
    pt_chr = chr(ord(ct_chr) ^ key)

    # 5. 发送答案 (注意：不能用 sendline，因为 input().strip() 会把换行吃掉，但稳妥起见直接发字符)
    p.sendline(pt_chr.encode())

    log.success(f"密文: {ct_chr}, Key: {hex(key)} => 明文: {pt_chr}")

# 拿下 Flag 并保持交互
p.interactive()

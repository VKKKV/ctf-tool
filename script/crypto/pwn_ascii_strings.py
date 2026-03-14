from pwn import *
from pwn import log, process, xor

context.log_level = "info"

# 核心技巧：使用 process.PTY 完美伪装成真实终端，绕过 isatty() 检查
p = process(["/challenge/run"], stdin=process.PTY, stdout=process.PTY)

for i in range(1, 10):
    log.info(f"正在破解第 {i} 关...")

    p.recvuntil(b"- Encrypted String: ")
    ct_str = p.recvline().strip()

    # 2. 解析 XOR Key
    p.recvuntil(b"- XOR Key String: ")
    key_str = p.recvline().strip()

    # 3. 等待输入提示符
    p.recvuntil(b"- Decrypted String? ")

    pt_str = xor(ct_str, key_str)

    # 5. 发送答案 (注意：不能用 sendline，因为 input().strip() 会把换行吃掉，但稳妥起见直接发字符)
    p.sendline(pt_str.decode())

    log.success(f"密文: {ct_str}, Key: {key_str} => 明文: {pt_str}")

p.interactive()

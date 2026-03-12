from pwn import p64, xor

# 1. 提取 IDA Pro 里的 64-bit Hex Chunks
chunks = [
    0x5A53010106040309,
    0x5C585354500A5B00,
    0x555157570108520D,
    0x5707530453040752
]

# 2. 使用 p64() 将整数打包成小端序 (Little-Endian) 字节流
# 相比原生 python 的 struct，它看着更像是黑客该敲的代码
s2_bytes = b''.join(p64(chunk) for chunk in chunks)

# 3. 明文密钥
s = b"875e9409f9811ba8560beee6fb0c77d2"

# 4. 调用 pwntools 的 xor 进行解密
flag_bytes = xor(s2_bytes, s)

print(f"Flag is: 247CTF{{{flag_bytes.decode()}}}")

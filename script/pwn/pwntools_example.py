#!/usr/bin/env python3

import json

from pwn import *  # pip install pwntools
from pwn import remote, process, p32, p64, u32

HOST = "socket.cryptohack.org"
PORT = 11112
# context.arch = 'amd64'
# context.endian = 'little' # or 'big'

r = remote(HOST, PORT)
p = process("./vuln")


def json_recv():
    line = r.recvline()
    return json.loads(line.decode())


def json_send(hsh):
    request = json.dumps(hsh).encode()
    r.sendline(request)


print(r.recvline())
print(r.recvline())
print(r.recvline())
print(r.recvline())

request = {"buy": "flag"}
json_send(request)

response = json_recv()

print(response)

hex_num = 0x12345678

# 转换成 Little-Endian (小端序) 的字节流
little_bytes = p32(hex_num, endian='little')
print(little_bytes) # 输出: b'\x78\x56\x34\x12'

# 转换成 Big-Endian (大端序) 的字节流
big_bytes = p32(hex_num, endian='big')
print(big_bytes)    # 输出: b'\x12\x34\x56\x78'

# 如果你想把字节流转回整数 (解包)
# u32() 同样支持 endian 参数
recovered_num = u32(little_bytes, endian='little')
print(hex(recovered_num)) # 输出: 0x12345678

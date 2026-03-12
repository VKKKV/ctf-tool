import os

import r2pipe

# 依然保持 Arch 的优雅，屏蔽 Wine 垃圾信息
os.environ["WINEDEBUG"] = "-all"

# 1. 启动时直接通过管道喂入一串足够长的伪造输入（比如 32 个 'A'）
# 使用 rarun2 配置文件是更高级的做法，但这里我们直接用 shell 技巧
r2 = r2pipe.open("flag_errata.exe", flags=["-d"])

# 2. 这里的策略是：先让程序运行到 main，然后直接把数据写入 stdin 缓冲区
r2.cmd("dcu main")

# 模拟输入：假设程序在等待 flag 格式输入
# 我们可以直接用 r2 的 'dx' 命令或者通过系统层面的 'w' 写入
# 但最简单的是在 dc 之前，确保你手动在终端敲了一下回车，或者：
# r2.cmd('".\n" | dcl') # 这是一个尝试喂入输入的黑科技命令

print("[*] I use Arch btw. 注入伪造输入并接管执行流...")

# ... (接之前的偏移计算逻辑) ...
OFFSET = 0x3125
base_addr = r2.cmdj("iSj")[0]["vaddr"]
TARGET_ADDR = hex(base_addr + OFFSET)

r2.cmd(f"db {TARGET_ADDR}")

flag = ""
for i in range(64):
    # 如果 dc 卡住，通常是在等输入
    # 你可以在运行脚本的终端手动敲入一些字符并回车
    r2.cmd("dc")

    regs = r2.cmdj("drj")
    if not regs or (regs.get("rip") or regs.get("eip")) != int(TARGET_ADDR, 16):
        # 如果没停在断点，可能还在等输入，尝试发送一个换行
        continue

    if "edx" in regs:
        char_val = regs["edx"] & 0xFF
        if 32 <= char_val <= 126:
            flag += chr(char_val)
            print(f"[+] 实时解密碎片: {flag}")

    r2.cmd("dr zf=1")
    r2.cmd("ds")

print(f"\n[!] 最终 Flag: {flag}")
r2.quit()

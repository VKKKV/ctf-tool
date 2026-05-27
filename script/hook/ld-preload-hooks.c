/*
 * ld-preload-hooks.c — 通用 LD_PRELOAD Hook 库
 *
 * 用法:
 *   gcc -Wall -shared -fPIC -ldl -o hook.so ld-preload-hooks.c -DENABLE_ALL
 *   LD_PRELOAD=./hook.so ./target
 *
 * 条件编译:
 *   -DENABLE_ALL      启所有hook
 *   -DENABLE_STRCMP   strcmp() 打印参数 + 可选返回0
 *   -DENABLE_PTRACE   ptrace() 返回0 (PTRACE_TRACEME 反调试绕过)
 *   -DENABLE_FOPEN    fopen() 打印路径+模式
 *   -DENABLE_OPEN     open() 打印路径+标志
 *   -DENABLE_CONNECT  connect() 打印目标IP:端口
 *   -DENABLE_RAND     rand() 返回固定值4
 *   -DENABLE_TIME     time() 返回固定值
 *   -DENABLE_GETENV   getenv() 打印变量名
 *   -DENABLE_SLEEP    sleep() 跳过等待
 *   -DENABLE_WRITE    write() 打印内容和长度
 *   -DENABLE_READ     read() 打印读取内容
 *   -DENABLE_SYSTEM   system() 打印并执行
 *
 * 环境变量控制:
 *   HACK_STRCMP_EQ=1  strcmp 始终返回0(密码绕过)
 *
 * 参考:
 *   https://axcheron.github.io/playing-with-ld-preload/
 *   https://github.com/jasperla/ (Common CTF functions for LD_PRELOAD)
 *   https://github.com/poliva/ldpreloadhook
 *   https://github.com/zommiommy/LDmitm
 *   https://tbrindus.ca/correct-ld-preload-hooking-libc/
 *   https://docs.xanhacks.xyz/reverse/hook/
 */

#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <dlfcn.h>
#include <stdarg.h>
#include <unistd.h>
#include <sys/types.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include <time.h>
#include <sys/ptrace.h>
#include <fcntl.h>

/* ================================================================
 * 辅助: 获取原始函数指针 (延迟加载, 避免 constructor 顺序问题)
 * ================================================================ */
#define GET_REAL(name)                                                  \
    static int (*real_##name)(void);                                    \
    if (!real_##name) {                                                 \
        real_##name = dlsym(RTLD_NEXT, #name);                          \
    }

/* ================================================================
 * 1. STRCHCMP — 打印比较参数
 * ================================================================ */
#if defined(ENABLE_STRCMP) || defined(ENABLE_ALL)

int strcmp(const char *s1, const char *s2) {
    static int (*real_strcmp)(const char *, const char *) = NULL;
    if (!real_strcmp) real_strcmp = dlsym(RTLD_NEXT, "strcmp");

    fprintf(stderr, "[HOOK strcmp] '%s' vs '%s'\n", s1 ? s1 : "(null)", s2 ? s2 : "(null)");

    if (getenv("HACK_STRCMP_EQ")) {
        return 0;  // 始终相等
    }
    return real_strcmp(s1, s2);
}

int strncmp(const char *s1, const char *s2, size_t n) {
    static int (*real_strncmp)(const char *, const char *, size_t) = NULL;
    if (!real_strncmp) real_strncmp = dlsym(RTLD_NEXT, "strncmp");

    fprintf(stderr, "[HOOK strncmp] '%.*s' vs '%.*s' (%zu)\n", (int)n, s1, (int)n, s2, n);

    if (getenv("HACK_STRCMP_EQ")) {
        return 0;
    }
    return real_strncmp(s1, s2, n);
}

#endif

/* ================================================================
 * 2. PTRACE — 绕过反调试 (返回 0 假装无调试器)
 * ================================================================ */
#if defined(ENABLE_PTRACE) || defined(ENABLE_ALL)

long ptrace(enum __ptrace_request request, ...) {
    fprintf(stderr, "[HOOK ptrace] request=%d -> 0\n", (int)request);
    return 0;
}

#endif

/* ================================================================
 * 3. FOPEN — 打印文件打开路径
 * ================================================================ */
#if defined(ENABLE_FOPEN) || defined(ENABLE_ALL)

FILE *fopen(const char *pathname, const char *mode) {
    static FILE *(*real_fopen)(const char *, const char *) = NULL;
    if (!real_fopen) real_fopen = dlsym(RTLD_NEXT, "fopen");

    fprintf(stderr, "[HOOK fopen] '%s' mode=%s\n", pathname ? pathname : "(null)", mode ? mode : "(null)");
    return real_fopen(pathname, mode);
}

#endif

/* ================================================================
 * 4. OPEN — 打印系统调用级别的文件打开
 * ================================================================ */
#if defined(ENABLE_OPEN) || defined(ENABLE_ALL)

int open(const char *pathname, int flags, ...) {
    static int (*real_open)(const char *, int, ...) = NULL;
    if (!real_open) real_open = dlsym(RTLD_NEXT, "open");

    mode_t mode = 0;
    if (flags & O_CREAT) {
        va_list args;
        va_start(args, flags);
        mode = va_arg(args, mode_t);
        va_end(args);
    }

    int fd = real_open(pathname, flags, mode);
    fprintf(stderr, "[HOOK open] '%s' flags=%o -> fd=%d\n",
            pathname ? pathname : "(null)", flags, fd);
    return fd;
}

#endif

/* ================================================================
 * 5. CONNECT — 打印网络连接目标 (分析反向 shell/网络行为)
 * ================================================================ */
#if defined(ENABLE_CONNECT) || defined(ENABLE_ALL)

int connect(int sockfd, const struct sockaddr *addr, socklen_t addrlen) {
    static int (*real_connect)(int, const struct sockaddr *, socklen_t) = NULL;
    if (!real_connect) real_connect = dlsym(RTLD_NEXT, "connect");

    char buf[64] = {0};
    int port = 0;

    if (addr->sa_family == AF_INET) {
        struct sockaddr_in *in = (struct sockaddr_in *)addr;
        inet_ntop(AF_INET, &in->sin_addr, buf, sizeof(buf));
        port = ntohs(in->sin_port);
    } else if (addr->sa_family == AF_INET6) {
        struct sockaddr_in6 *in6 = (struct sockaddr_in6 *)addr;
        inet_ntop(AF_INET6, &in6->sin6_addr, buf, sizeof(buf));
        port = ntohs(in6->sin6_port);
    } else {
        snprintf(buf, sizeof(buf), "family=%d", addr->sa_family);
    }

    fprintf(stderr, "[HOOK connect] fd=%d -> %s:%d\n", sockfd, buf, port);
    return real_connect(sockfd, addr, addrlen);
}

#endif

/* ================================================================
 * 6. RAND — 固定随机数 (绕过依赖随机的检查)
 * ================================================================ */
#if defined(ENABLE_RAND) || defined(ENABLE_ALL)

int rand(void) {
    fprintf(stderr, "[HOOK rand] -> 4 (chosen by fair dice roll)\n");
    return 4;
}

#endif

/* ================================================================
 * 7. TIME — 固定时间
 * ================================================================ */
#if defined(ENABLE_TIME) || defined(ENABLE_ALL)

time_t time(time_t *t) {
    time_t fake = 1234567890;  // 2009-02-13
    fprintf(stderr, "[HOOK time] -> %ld\n", (long)fake);
    if (t) *t = fake;
    return fake;
}

#endif

/* ================================================================
 * 8. GETENV — 打印环境变量读取 (检测程序在查什么)
 * ================================================================ */
#if defined(ENABLE_GETENV) || defined(ENABLE_ALL)

char *getenv(const char *name) {
    static char *(*real_getenv)(const char *) = NULL;
    if (!real_getenv) real_getenv = dlsym(RTLD_NEXT, "getenv");

    char *val = real_getenv(name);
    fprintf(stderr, "[HOOK getenv] '%s' -> %s\n",
            name ? name : "(null)", val ? val : "(null)");
    return val;
}

#endif

/* ================================================================
 * 9. SLEEP / USLEEP — 跳过等待
 * ================================================================ */
#if defined(ENABLE_SLEEP) || defined(ENABLE_ALL)

unsigned int sleep(unsigned int seconds) {
    fprintf(stderr, "[HOOK sleep] %u -> skipped\n", seconds);
    return 0;
}

int usleep(useconds_t usec) {
    fprintf(stderr, "[HOOK usleep] %lu -> skipped\n", (unsigned long)usec);
    return 0;
}

#endif

/* ================================================================
 * 10. WRITE — 打印写操作 (观察程序输出)
 * ================================================================ */
#if defined(ENABLE_WRITE) || defined(ENABLE_ALL)

ssize_t write(int fd, const void *buf, size_t count) {
    static ssize_t (*real_write)(int, const void *, size_t) = NULL;
    if (!real_write) real_write = dlsym(RTLD_NEXT, "write");

    ssize_t ret = real_write(fd, buf, count);

    if (fd <= 2) {  // stdin/stdout/stderr
        // 不拦截标准 fd 避免死循环
    } else {
        fprintf(stderr, "[HOOK write] fd=%d len=%zu -> %zd\n", fd, count, ret);
    }
    return ret;
}

#endif

/* ================================================================
 * 11. SYSTEM — 打印执行的命令 (检测 system() 调用)
 * ================================================================ */
#if defined(ENABLE_SYSTEM) || defined(ENABLE_ALL)

int system(const char *command) {
    static int (*real_system)(const char *) = NULL;
    if (!real_system) real_system = dlsym(RTLD_NEXT, "system");

    fprintf(stderr, "[HOOK system] '%s'\n", command ? command : "(null)");
    return real_system(command);
}

#endif

/* ================================================================
 * 12. PUTS — 打印 plus 调用 (轻量级信息)
 * ================================================================ */
#if defined(ENABLE_PUTS) || defined(ENABLE_ALL)

int puts(const char *s) {
    static int (*real_puts)(const char *) = NULL;
    if (!real_puts) real_puts = dlsym(RTLD_NEXT, "puts");

    fprintf(stderr, "[HOOK puts] '%s'\n", s ? s : "(null)");
    return real_puts(s);
}

#endif

/* ================================================================
 * 初始化
 * ================================================================ */
__attribute__((constructor))
static void init(void) {
    const char *flags[] = {
#if defined(ENABLE_ALL)
        "ALL",
#endif
#if defined(ENABLE_STRCMP)
        "STRCMP",
#endif
#if defined(ENABLE_PTRACE)
        "PTRACE",
#endif
#if defined(ENABLE_FOPEN)
        "FOPEN",
#endif
#if defined(ENABLE_OPEN)
        "OPEN",
#endif
#if defined(ENABLE_CONNECT)
        "CONNECT",
#endif
#if defined(ENABLE_RAND)
        "RAND",
#endif
#if defined(ENABLE_TIME)
        "TIME",
#endif
#if defined(ENABLE_GETENV)
        "GETENV",
#endif
#if defined(ENABLE_SLEEP)
        "SLEEP",
#endif
#if defined(ENABLE_WRITE)
        "WRITE",
#endif
#if defined(ENABLE_SYSTEM)
        "SYSTEM",
#endif
#if defined(ENABLE_PUTS)
        "PUTS",
#endif
        NULL
    };

    fprintf(stderr, "[LD_PRELOAD hook loaded] enabled:");
    for (int i = 0; flags[i]; i++)
        fprintf(stderr, " %s", flags[i]);
    fprintf(stderr, "\n");
}

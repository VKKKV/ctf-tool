/*
 * hook-memdump.c — LD_PRELOAD hook: dump printable strings from readable memory
 *
 * 场景: binary 有 x 权限但无 r 权限 (e.g. ---x--x---)
 * 只能执行不能读。利用 LD_PRELOAD 从进程内部 dump 自身内存。
 *
 * 编译:
 *   gcc -m32 -shared -fPIC -o hook-memdump.so hook-memdump.c
 *   gcc -m64 -shared -fPIC -o hook-memdump.so hook-memdump.c
 *   (用 -m32 还是 -m64 取决于目标 binary 是 32 还是 64 位)
 *
 * 用法:
 *   LD_PRELOAD=./hook-memdump.so /path/to/binary 2>&1
 *
 * 原理:
 *   替换 puts()/write() 等输出函数，先遍历 /proc/self/maps 中所有
 *   可读段，dump 其中的 printable ASCII 字符串到 stderr。
 *   然后调用真实函数确保程序正常输出。
 *
 * 策略:
 *   - 只 dump 一次（static done 标志），避免重复
 *   - 跳过不可读段 (perms[0] != 'r')
 *   - 对每个可读段，步进 16 字节，遇到连续 printable 就整体输出
 *   - 不 dump 标准输出（避免无限递归）
 *
 * 参考: OverTheWire Utumno Level 0
 *   Binary exec-only, puts(password_string) 在 rodata 段。
 *   不需要猜地址——直接从 maps 确定所有可读段。
 */

#define _GNU_SOURCE
#include <stdio.h>
#include <ctype.h>
#include <string.h>
#include <dlfcn.h>
#include <unistd.h>

static int mem_dumped = 0;

static void dump_readable_strings(void) {
    if (mem_dumped) return;
    mem_dumped = 1;

    FILE *maps = fopen("/proc/self/maps", "r");
    if (!maps) return;

    char line[512];
    while (fgets(line, sizeof(line), maps)) {
        unsigned long start, end;
        char perms[8];
        if (sscanf(line, "%lx-%lx %7s", &start, &end, perms) < 3)
            continue;

        // 只扫可读段
        if (perms[0] != 'r') continue;

        // 跳过 stack/vvar/vdso 等噪声段
        if (strstr(line, "[stack]") || strstr(line, "[vvar]") ||
            strstr(line, "[vdso]") || strstr(line, "[vsyscall]") ||
            strstr(line, "[vvar]"))
            continue;

        for (unsigned long addr = start; addr < end; ) {
            // 找 printable 串起点
            int is_print = 1;
            int slen = 0;
            for (unsigned long p = addr; p < end && p - addr < 256; p++) {
                char c = *(volatile char *)p;
                if (c == '\0') break;
                if (!isprint((unsigned char)c)) { is_print = 0; break; }
                slen++;
            }

            if (is_print && slen >= 4) {
                // 有意义的 printable 串 → 整体输出
                // 用 write() 直接写 stderr 避免递归
                write(2, (const void *)addr, slen);
                write(2, "\n", 1);
                addr += slen;
            } else {
                addr += 16;
            }
        }
    }
    fclose(maps);
}

/*
 * hook write()——拦截对 stdout 的写入时触发 dump
 * 但注意: 不能在写 stderr 时也 dump，会递归
 */
ssize_t write(int fd, const void *buf, size_t count) {
    static ssize_t (*real_write)(int, const void *, size_t) = NULL;
    if (!real_write) real_write = dlsym(RTLD_NEXT, "write");

    // 只对 stdout/stderr 触发一次 dump
    if (fd <= 2 && !mem_dumped) {
        dump_readable_strings();
    }

    return real_write(fd, buf, count);
}

/*
 * hook puts()——puts 通常由 binary 调用，触发时机好
 */
int puts(const char *s) {
    static int (*real_puts)(const char *) = NULL;
    if (!real_puts) real_puts = dlsym(RTLD_NEXT, "puts");

    if (!mem_dumped) {
        dump_readable_strings();
    }

    return real_puts(s);
}

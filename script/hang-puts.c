/*
 * hang.c — LD_PRELOAD hook to make a process stay alive for pmap
 *
 * Usage:
 *   gcc -shared -fPIC -o hang.so hang.c
 *   LD_PRELOAD=./hang.so /utumno/utumno0 &
 *   PID=$!
 *   sleep 0.5
 *   pmap $PID
 *   kill $PID
 */

#include <unistd.h>

/* hook 第一个被调用的库函数，让程序暂停 60 秒 */
int puts(const char *s) {
    sleep(60);
    return 0;
}

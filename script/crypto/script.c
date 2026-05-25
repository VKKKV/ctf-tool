/*
 * encrypt6 — 8-bit LFSR stream cipher (A-Z only)
 *
 * 模拟 OverTheWire Krypton level 5→6 的加密工具。
 *
 * 原理：
 *   - 8 位 Galois LFSR，以 keyfile.dat 的首字节为种子
 *   - 每加密一个字母，LFSR 走一步，输出 8-bit 状态
 *   - 输出字节映射到 0-25：shift = state % 26
 *   - 加密：cipher = (plain - 'A' + shift) % 26 + 'A'
 *
 * 已知特性：
 *   - 周期 255（全零态锁死，跳过）
 *   - 字母输出上观察到的周期 30（由 mod 26 产生）
 *   - 已知明文攻击：加密 'A'*N 直接恢复 keystream
 *
 * 验证 keystream（对 'A' 加密的输出）：
 *   EICTDGYIYZKTHNSIRFXYCPFUEOCKRN (重复)
 *
 * 编译：gcc -o encrypt6 script.c
 * 使用：./encrypt6 <plain.txt >cipher.txt
 *       或 ./encrypt6 <plain.txt cipher.txt
 */

#include <stdio.h>
#include <stdint.h>
#include <stdlib.h>
#include <ctype.h>

/* ------------------------------------------------------------------ */
/*  8-bit Galois LFSR                                                 */
/* ------------------------------------------------------------------ */

/*
 * 多项式 x^8 + x^4 + x^3 + x^2 + 1  (Xilinx XAPP 052)
 *
 * 标准形式：x^8 + x^4 + x^3 + x^2 + 1
 * Galois 掩码：0x1D  (bit3=x^4, bit2=x^3, bit1=x^2, bit0=x^0)
 *            bit7  bit6  bit5  bit4  bit3  bit2  bit1  bit0
 *             0     0     0     1     1     1     0     1   = 0x1D
 *
 * 其他常见 8 位本原多项式（若需替换）：
 *   x^8 + x^5 + x^3 + x^1 + 1  → 0x2B
 *   x^8 + x^6 + x^5 + x^4 + 1  → 0x71
 *   x^8 + x^6 + x^5 + x^3 + 1  → 0x69
 */
#define LFSR_POLY   0x1D

struct lfsr {
    uint8_t state;  /* 当前 8-bit 状态 */
};

/* 初始化：种子必须非零（全零是锁死态） */
static void lfsr_init(struct lfsr *r, uint8_t seed)
{
    r->state = seed ? seed : 1;
}

/* 走一步，返回新状态 */
static uint8_t lfsr_step(struct lfsr *r)
{
    uint8_t lsb = r->state & 1;
    r->state >>= 1;
    if (lsb)
        r->state ^= LFSR_POLY;
    return r->state;
}

/* ------------------------------------------------------------------ */
/*  A-Z stream cipher                                                  */
/* ------------------------------------------------------------------ */

/*
 * 将 LFSR 输出字节映射到 0-25（A-Z 的移位量）。
 * state % 26 够用，dist 不太均匀但简单。
 */
static int keystream_byte(struct lfsr *r)
{
    return lfsr_step(r) % 26;
}

int main(int argc, char *argv[])
{
    FILE *fin  = stdin;
    FILE *fout = stdout;

    if (argc > 3) {
        fprintf(stderr, "Usage: %s [<infile> [<outfile>]]\n", argv[0]);
        return 1;
    }
    if (argc >= 2) {
        fin = fopen(argv[1], "r");
        if (!fin) { perror(argv[1]); return 1; }
    }
    if (argc >= 3) {
        fout = fopen(argv[2], "w");
        if (!fout) { perror(argv[2]); return 1; }
    }

    /* ---- 读取种子（keyfile.dat） ---- */
    FILE *fk = fopen("keyfile.dat", "r");
    uint8_t seed = 0xE1;    /* 兜底默认值 */
    if (fk) {
        int c = fgetc(fk);
        if (c != EOF) seed = (uint8_t)c;
        fclose(fk);
    } else {
        fprintf(stderr, "warning: keyfile.dat not found, using default seed 0x%02X\n", seed);
    }

    struct lfsr r;
    lfsr_init(&r, seed);

    /* ---- 逐字符加密 ---- */
    int c;
    while ((c = fgetc(fin)) != EOF) {
        if (!isalpha((unsigned char)c)) {
            /* 非字母原样输出（空格、换行等） */
            fputc(c, fout);
            continue;
        }
        int base = isupper(c) ? 'A' : 'a';
        int p    = c - base;              /* 0-25 */
        int k    = keystream_byte(&r);    /* 0-25 */
        int enc  = (p + k) % 26;          /* 加密 */
        fputc(enc + base, fout);
    }

    if (fin  != stdin)  fclose(fin);
    if (fout != stdout) fclose(fout);
    return 0;
}

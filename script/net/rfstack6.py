#!/usr/bin/env python3
import sys

import matplotlib.pyplot as plt
import numpy as np


def main():
    filepath = "/home/kita/Downloads/needle/hint1.cf32"
    print(f"[*] Loading raw baseband from {filepath}...")
    iq_data = np.fromfile(filepath, dtype=np.complex64)

    # 确定的绝对起跑线
    OFFSET = 153600
    NFFT = 1024

    # 我们打赌出题人偷懒了，用了一个最标准的恒定 72 长度 CP
    CP_LEN = 72

    print("[*] Performing Single-Symbol Surgical Extraction...")

    # 仅仅提取第 0 个符号的实际数据区（跳过前面的 CP）
    start_idx = OFFSET + CP_LEN
    symbol_time = iq_data[start_idx : start_idx + NFFT]

    # 变换到频域
    symbol_freq = np.fft.fftshift(np.fft.fft(symbol_time))

    # 【核心修复】：根据瀑布图严格限制子载波范围
    # 瀑布图中心是 512。信号大概覆盖 342 到 682 (总宽 ~340)
    # 过滤掉正中心的 512 (DC 直流载波，通常为空白或带噪)
    active_subcarriers = np.concatenate(
        [
            symbol_freq[512 - 170 : 512],  # 左侧 170 个
            symbol_freq[512 + 1 : 512 + 171],  # 右侧 170 个
        ]
    )

    print(f"[+] Extracted exactly {len(active_subcarriers)} pure data subcarriers.")

    # 画图
    print("[*] Rendering Single-Symbol Constellation...")
    fig, ax = plt.subplots(figsize=(6, 6), facecolor="#1e1e2e")

    ax.scatter(
        active_subcarriers.real,
        active_subcarriers.imag,
        s=15,
        color="#f38ba8",
        alpha=0.9,
        marker="x",
    )  # 用大一点的红色 X，看个清楚

    ax.set_title(f"Symbol 0 Pure Constellation (No Drift)", color="#cdd6f4")
    ax.set_xlabel("In-Phase (I)", color="#cdd6f4")
    ax.set_ylabel("Quadrature (Q)", color="#cdd6f4")
    ax.grid(True, color="#45475a", linestyle="--")
    ax.tick_params(colors="#cdd6f4")

    ax.axhline(0, color="#89b4fa", linewidth=0.5)
    ax.axvline(0, color="#89b4fa", linewidth=0.5)

    # 放开坐标轴限制，让自适应缩放展示真实的幅度
    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    main()

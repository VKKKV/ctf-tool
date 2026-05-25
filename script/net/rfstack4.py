#!/usr/bin/env python3
import sys

import matplotlib.pyplot as plt
import numpy as np


def read_iq(filepath):
    print(f"[*] Reading pure baseband data from {filepath}...")
    return np.fromfile(filepath, dtype=np.complex64)


def plot_precise_sync(iq_data, nfft=1024, cp_len=72):
    print("[*] Compiling normalized CP correlation matrix...")

    # 1. 延迟 NFFT 个采样点
    # 这相当于我们在拿符号的“尾部”去跟“头部”做基因比对
    delayed_iq = np.roll(iq_data, -nfft)

    # 2. 共轭相乘
    mult = iq_data * np.conj(delayed_iq)

    # 3. 滑动窗口求和 (The Arch Way: 向量化卷积，极其快速)
    window = np.ones(cp_len)
    corr = np.convolve(mult, window, mode="valid")

    # 4. 计算局部能量用于归一化
    energy = np.convolve(np.abs(iq_data) ** 2, window, mode="valid")

    # 5. 计算归一化的相关度量度 (0.0 ~ 1.0)
    metric = np.abs(corr) / (energy + 1e-10)

    print("[*] Plotting precision timing metric...")
    fig, ax = plt.subplots(figsize=(14, 5), facecolor="#1e1e2e")

    ax.plot(metric, color="#89b4fa", linewidth=0.8)

    ax.set_title(
        "Strict CP Correlation Metric (Find the EXACT start sample)", color="#cdd6f4"
    )
    ax.set_ylabel("Correlation Coefficient (0 to 1)", color="#cdd6f4")
    ax.set_xlabel("Sample Index", color="#cdd6f4")
    ax.grid(True, color="#45475a", linestyle="--")
    ax.tick_params(colors="#cdd6f4")

    # 画一条 0.5 的参考线，超过这个线的基本就是真正的信号开始了
    ax.axhline(0.5, color="#f38ba8", linestyle=":", linewidth=1)

    plt.tight_layout()
    plt.show()


def main():
    filepath = "/home/kita/Downloads/needle/hint1.cf32"  # 确保路径正确
    iq_data = read_iq(filepath)

    # 我们先用标准的 72 长度去探测
    plot_precise_sync(iq_data, nfft=1024, cp_len=72)


if __name__ == "__main__":
    main()

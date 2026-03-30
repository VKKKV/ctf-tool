#!/usr/bin/env python3
import sys

import matplotlib.pyplot as plt
import numpy as np


def main():
    filepath = "/home/kita/Downloads/needle/hint1.cf32"
    print(f"[*] Reading pure baseband data from {filepath}...")
    iq_data = np.fromfile(filepath, dtype=np.complex64)

    # 绝对精准的偏移量 (The Precision Cut)
    OFFSET = 153600
    NFFT = 1024

    # 截断前面的 10ms 垃圾帧，直奔主题
    payload_data = iq_data[OFFSET:]

    print("[*] Performing strict LTE-compliant symbol slicing...")
    constellation = []
    idx = 0
    sym_count = 0

    # 我们先提取前 50 个符号看看成色（避免把尾部的噪声也切进去）
    while idx + NFFT + 80 <= len(payload_data) and sym_count < 50:
        # LTE Normal CP 规则：每 7 个符号一个循环，第 0 个是 80，其余 72
        cp_len = 80 if (sym_count % 7 == 0) else 72

        # 精准剥离 CP
        symbol_time = payload_data[idx + cp_len : idx + cp_len + NFFT]

        # 变换到频域并居中
        symbol_freq = np.fft.fftshift(np.fft.fft(symbol_time))

        # 过滤掉 DC 载波和两侧的 Guard Bands
        # LTE 10MHz 有用的载波大约在中心 ±300，为了保险我们取宽一点
        # 但坚决不要正中心的 DC (NFFT/2)
        useful_subcarriers = np.concatenate(
            [
                symbol_freq[NFFT // 2 - 300 : NFFT // 2 - 1],  # 负频段活跃载波
                symbol_freq[NFFT // 2 + 1 : NFFT // 2 + 301],  # 正频段活跃载波
            ]
        )

        constellation.append(useful_subcarriers)

        idx += NFFT + cp_len
        sym_count += 1

    # 拍扁成一维复数数组
    constellation = np.concatenate(constellation)
    print(
        f"[+] Decoded {sym_count} symbols. Extracted {len(constellation)} subcarriers."
    )

    print("[*] Rendering Phase/Amplitude Diagram...")
    fig, ax = plt.subplots(figsize=(8, 8), facecolor="#1e1e2e")

    # 绘制真正的星座图
    ax.scatter(constellation.real, constellation.imag, s=2, color="#a6e3a1", alpha=0.5)

    ax.set_title(f"Perfect Synchronization Constellation ({filepath})", color="#cdd6f4")
    ax.set_xlabel("In-Phase (I)", color="#cdd6f4")
    ax.set_ylabel("Quadrature (Q)", color="#cdd6f4")
    ax.grid(True, color="#45475a", linestyle="--")
    ax.tick_params(colors="#cdd6f4")

    ax.axhline(0, color="#f38ba8", linewidth=0.5)
    ax.axvline(0, color="#f38ba8", linewidth=0.5)

    # 限制一下坐标系范围，防止几个极端噪声点拉大整个图表
    ax.set_xlim(-15, 15)
    ax.set_ylim(-15, 15)

    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    main()

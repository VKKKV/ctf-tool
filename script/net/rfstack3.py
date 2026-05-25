#!/usr/bin/env python3
import sys

import matplotlib.pyplot as plt
import numpy as np


def read_iq(filepath):
    print(f"[*] Reading pure baseband data from {filepath}...")
    return np.fromfile(filepath, dtype=np.complex64)


def extract_resource_grid(iq_data, nfft=1024):
    """
    按照 LTE 物理层规范 (Normal CP) 提取资源网格。
    拒绝一切黑盒猜测，精准操控每一个采样点。
    """
    print("[*] Slicing OFDM symbols based on LTE slot structure...")
    grid = []
    idx = 0
    sym_count = 0

    # 只要剩下的数据还够切一个带最小 CP 的符号，就继续切
    while idx + nfft + 80 <= len(iq_data):
        # 核心逻辑：每 7 个符号为一个 Slot，第 0 个 CP 为 80，其余为 72
        cp_len = 80 if (sym_count % 7 == 0) else 72

        # 1. 剔除 CP 垃圾数据
        symbol_time = iq_data[idx + cp_len : idx + cp_len + nfft]

        # 2. 变换到频域并居中 DC 载波
        symbol_freq = np.fft.fftshift(np.fft.fft(symbol_time))
        grid.append(symbol_freq)

        # 3. 步进到下一个符号的绝对起始位置
        idx += nfft + cp_len
        sym_count += 1

    print(f"[+] Extracted {sym_count} symbols perfectly.")
    # 转置矩阵，让 Y 轴变成频率（子载波），X 轴变成时间（符号）
    return np.array(grid).T


def main():
    filepath = "/home/kita/Downloads/needle/hint1.cf32"
    iq_data = read_iq(filepath)

    # 提取整个 2D 资源网格
    grid = extract_resource_grid(iq_data)

    print("[*] Performing surgical slicing on the Resource Grid...")
    # The Arch Way: 极简切片，拒绝臃肿
    # 根据我们瀑布图的视觉坐标，把无用的 bloat 全部砍掉
    # Y 轴 (频率/子载波): 大约从 340 到 680
    # X 轴 (时间/符号): 大约从 140 到 168

    # 注意：NumPy 数组切片是 [Y_start:Y_end, X_start:X_end]
    clean_payload = grid[340:680, 140:168]

    # 把二维矩阵拍扁成一维数组的复数点
    constellation = clean_payload.flatten()

    print(f"[+] Extracted {len(constellation)} pure complex symbols.")

    # 绘制最终的星座图
    print("[*] Plotting the Final Constellation diagram...")
    fig, ax = plt.subplots(figsize=(6, 6), facecolor="#1e1e2e")

    ax.scatter(constellation.real, constellation.imag, s=2, color="#a6e3a1", alpha=0.8)
    ax.set_title(f"Pure Payload Constellation ({filepath})", color="#cdd6f4")
    ax.set_xlabel("In-Phase (I)", color="#cdd6f4")
    ax.set_ylabel("Quadrature (Q)", color="#cdd6f4")
    ax.grid(True, color="#45475a", linestyle="--")
    ax.tick_params(colors="#cdd6f4")

    # 画两条十字线辅助观察
    ax.axhline(0, color="#f38ba8", linewidth=0.5)
    ax.axvline(0, color="#f38ba8", linewidth=0.5)

    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    main()

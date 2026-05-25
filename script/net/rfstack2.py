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

    grid = extract_resource_grid(iq_data)

    print("[*] Rendering Resource Grid waterfall diagram...")
    fig, ax = plt.subplots(figsize=(12, 6), facecolor="#1e1e2e")

    # 计算功率 (以 dB 为单位，防止极值拉低对比度)
    power_db = 10 * np.log10(np.abs(grid) ** 2 + 1e-12)

    # 绘制热力图 (使用 magma 配色，这很有 Hacker 的感觉)
    im = ax.imshow(
        power_db,
        aspect="auto",
        origin="lower",
        cmap="magma",
    )

    ax.set_title("OFDM Resource Grid (Subcarrier Allocation)", color="#cdd6f4")
    ax.set_ylabel("Subcarrier Index (Centered at DC)", color="#cdd6f4")
    ax.set_xlabel("OFDM Symbol Index (Time)", color="#cdd6f4")
    ax.tick_params(colors="#cdd6f4")

    cbar = fig.colorbar(im, ax=ax)
    cbar.set_label("Power (dB)", color="#cdd6f4")
    cbar.ax.yaxis.set_tick_params(color="#cdd6f4")
    plt.setp(plt.getp(cbar.ax.axes, "yticklabels"), color="#cdd6f4")

    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    main()

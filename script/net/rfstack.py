#!/usr/bin/env python3
import sys

import matplotlib.pyplot as plt
import numpy as np


def read_iq(filepath):
    """KISS 原则：直接把二进制文件读进内存，映射为复数。"""
    print(f"[*] Reading I/Q data from {filepath}...")
    return np.fromfile(filepath, dtype=np.complex64)


def find_symbol_sync(iq_data, nfft=1024, cp_len=72):
    """
    手动计算延迟自相关寻找 Cyclic Prefix (CP)。
    LTE 的标准 10MHz 配置通常是 NFFT=1024, Normal CP 长度为 72 左右。
    我们通过数学计算找出符号的绝对边界，不需要那些臃肿的黑盒 SDR 软件。
    """
    print("[*] Performing delayed autocorrelation for symbol synchronization...")
    # 计算延迟相关的能量
    correlation = np.zeros(len(iq_data) - nfft - cp_len, dtype=np.complex64)

    # 滑动窗口计算 (这里用了个暴力的循环，如果在生产环境我会用向量化或 C 扩展，但为了让你看懂核心逻辑先这样写)
    for i in range(len(correlation)):
        window = iq_data[i : i + cp_len]
        delayed_window = iq_data[i + nfft : i + nfft + cp_len]
        correlation[i] = np.sum(window * np.conj(delayed_window))

    # 取幅值
    corr_mag = np.abs(correlation)

    # 找到第一个相关性峰值，这通常标志着第一个 OFDM 符号的 CP 起始位置
    # 实际 CTF 中可能需要设置 threshold 过滤噪声，这里简单取全局最大值附近的点
    start_idx = np.argmax(corr_mag)
    print(f"[+] Found probable first symbol start at index: {start_idx}")

    return start_idx, corr_mag


def extract_constellation(iq_data, start_idx, nfft=1024, cp_len=72, num_symbols=10):
    """剥离 CP，执行 FFT，提取频域子载波上的星座点。"""
    print(f"[*] Extracting subcarriers via FFT for {num_symbols} symbols...")
    constellation = []

    idx = start_idx
    for _ in range(num_symbols):
        if idx + cp_len + nfft > len(iq_data):
            break

        # 1. 丢弃 CP (Bloat is bad, drop it)
        symbol_time = iq_data[idx + cp_len : idx + cp_len + nfft]

        # 2. 时域变频域 (Fast Fourier Transform)
        symbol_freq = np.fft.fftshift(np.fft.fft(symbol_time))

        # 将子载波数据存入列表
        constellation.append(symbol_freq)

        # 移动到下一个符号
        idx += nfft + cp_len

    return np.concatenate(constellation)


def main():
    filepath = "/home/kita/Downloads/for_user/hint1.cf32"

    # 基于前面推导的 LTE 10MHz 参数
    NFFT = 1024
    CP_LEN = 72  # 注意：LTE 的第一个 CP 可能是 80，后面是 72，这里先用 72 测试

    iq_data = read_iq(filepath)

    start_idx, corr_mag = find_symbol_sync(
        iq_data, NFFT, 72
    )  # 我们还是用标准配置先跑，为了画图

    print("[*] Plotting Delayed Autocorrelation for manual inspection...")
    # The Arch Way: 明确定义 Figure 和 Axes 对象，拒绝隐式状态机的混乱
    fig, ax = plt.subplots(figsize=(10, 4), facecolor="#1e1e2e")

    ax.plot(corr_mag[: NFFT * 5], color="#f38ba8")
    ax.set_title(f"Delayed Autocorrelation Function (hint1.cf32)", color="#cdd6f4")
    ax.set_ylabel("Correlation Magnitude", color="#cdd6f4")
    ax.set_xlabel("Sample Index (Time)", color="#cdd6f4")
    ax.grid(True, color="#45475a", linestyle="--")
    ax.set_facecolor("#1e1e2e")
    ax.tick_params(colors="#cdd6f4")

    plt.tight_layout()
    plt.show()

    sys.exit(0)  # 别忘了依然要在这里暂停！

    # 找同步点
    start_idx, corr_mag = find_symbol_sync(iq_data, NFFT, CP_LEN)

    # 提取并 FFT
    constellation = extract_constellation(
        iq_data, start_idx, NFFT, CP_LEN, num_symbols=20
    )

    # 绘制星座图
    print("[*] Plotting Constellation diagram. Minimal GUI initialized.")
    plt.figure(figsize=(8, 8), facecolor="#1e1e2e")  # 给点稍微顺眼一点的暗色主题
    ax = plt.axes()
    ax.set_facecolor("#1e1e2e")

    # 绘制散点
    plt.scatter(constellation.real, constellation.imag, s=1, color="#a6e3a1", alpha=0.5)
    plt.title(f"Constellation Diagram of {filepath}", color="#cdd6f4")
    plt.xlabel("In-Phase (I)", color="#cdd6f4")
    plt.ylabel("Quadrature (Q)", color="#cdd6f4")
    plt.grid(True, color="#45475a", linestyle="--")
    ax.tick_params(colors="#cdd6f4")

    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    main()

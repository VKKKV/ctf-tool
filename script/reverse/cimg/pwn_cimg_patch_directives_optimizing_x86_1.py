"""cIMG exploit: optimized x86 directive patching (variant 1)."""
import struct

from pwn import ELF, log, process


def extract_pixels_from_elf(binary_path, num_pixels):
    elf = ELF(binary_path, checksec=False)
    try:
        addr = elf.symbols["desired_output"]
    except KeyError:
        addr = 0x404020

    raw = elf.read(addr, num_pixels * 24)
    pixels = []
    for i in range(num_pixels):
        chunk = raw[i * 24 : (i + 1) * 24]
        try:
            r = int(chunk[7:10])
            g = int(chunk[11:14])
            b = int(chunk[15:18])
            c = chunk[19]
            pixels.append((r, g, b, c))
        except ValueError:
            pass
    return pixels


def build_payload():
    binary_path = "/challenge/cimg"
    num_pixels = 1824
    width = 76
    height = 24

    pixels = extract_pixels_from_elf(binary_path, num_pixels)
    if len(pixels) != num_pixels:
        log.error("Failed to extract full image. Check your binary.")
        return

    # 1. 提取所有前景像素
    fg_pixels = set()
    for y in range(height):
        for x in range(width):
            p = pixels[y * width + x]
            if p[3] not in (32, 10):  # 过滤空格和换行
                fg_pixels.add((x, y))

    log.info(f"Targeting {len(fg_pixels)} foreground pixels.")

    # 2. 暴力生成所有有价值的候选框 (Candidate Rectangles)
    candidates = []
    for x1 in range(width):
        for y1 in range(height):
            for x2 in range(x1, width):
                for y2 in range(y1, height):
                    # 快速找出框内的前景像素
                    cov = {
                        (x, y)
                        for x in range(x1, x2 + 1)
                        for y in range(y1, y2 + 1)
                        if (x, y) in fg_pixels
                    }
                    if not cov:
                        continue

                    cost = 6 + 4 * (x2 - x1 + 1) * (y2 - y1 + 1)
                    # 核心过滤：如果平均成本 > 10 (即不如单独 1x1 划算)，直接抛弃，拒绝 bloat
                    if cost <= 10 * len(cov):
                        candidates.append(
                            {
                                "rect": (x1, y1, x2 - x1 + 1, y2 - y1 + 1),
                                "cost": cost,
                                "cov": cov,
                            }
                        )

    # 3. 策略A: 基于性价比 (Cost / Covered) 的贪心算法
    uncovered_a = set(fg_pixels)
    blocks_a = []
    size_a = 12
    while uncovered_a:
        best_cand = None
        best_ratio = float("inf")
        for c in candidates:
            cov_now = c["cov"].intersection(uncovered_a)
            if not cov_now:
                continue
            ratio = c["cost"] / len(cov_now)
            if ratio < best_ratio or (
                ratio == best_ratio
                and len(cov_now)
                > (len(best_cand["cov"].intersection(uncovered_a)) if best_cand else 0)
            ):
                best_ratio = ratio
                best_cand = c

        assert best_cand is not None, "Failed to find best candidate"
        blocks_a.append(best_cand["rect"])
        uncovered_a -= best_cand["cov"]
        size_a += best_cand["cost"]

    # 4. 策略B: 基于绝对收益 (Profit) 的贪心算法 (作为 baseline 对照)
    uncovered_b = set(fg_pixels)
    blocks_b = []
    size_b = 12
    while uncovered_b:
        best_cand = None
        best_profit = -float("inf")
        for c in candidates:
            cov_now = c["cov"].intersection(uncovered_b)
            if not cov_now:
                continue
            profit = len(cov_now) * 10 - c["cost"]
            if profit > best_profit or (
                profit == best_profit
                and len(cov_now)
                > (len(best_cand["cov"].intersection(uncovered_b)) if best_cand else 0)
            ):
                best_profit = profit
                best_cand = c

        assert best_cand is not None, "Failed to find best candidate"
        blocks_b.append(best_cand["rect"])
        uncovered_b -= best_cand["cov"]
        size_b += best_cand["cost"]

    log.info(f"Strategy A (Ratio) estimated size: {size_a} bytes")
    log.info(f"Strategy B (Profit) estimated size: {size_b} bytes")

    # 优胜劣汰
    best_blocks = blocks_a if size_a < size_b else blocks_b
    log.success(
        f"Arch-level optimization selected the minimal set of {len(best_blocks)} blocks."
    )

    # 5. 组装 Payload
    directives_payload = bytearray()
    SUB_BLOCK_OPCODE = 52965

    for x, y, w, h in best_blocks:
        directives_payload += struct.pack("<H", SUB_BLOCK_OPCODE)
        directives_payload += struct.pack("<BBBB", x, y, w, h)
        for dy in range(h):
            for dx in range(w):
                p = pixels[(y + dy) * width + x + dx]
                directives_payload += struct.pack("<BBBB", p[0], p[1], p[2], p[3])

    total_size = len(directives_payload) + 12

    if total_size > 1337:
        log.error(
            f"Kernel Panic! Still too bloated. Over by {total_size - 1337} bytes."
        )
        return

    magic = b"cIMG"
    version = 3
    file_header = struct.pack(
        "<4sHBBI", magic, version, width, height, len(best_blocks)
    )

    payload = file_header + directives_payload
    file_name = "payload.cimg"
    with open(file_name, "wb") as f:
        f.write(payload)

    log.success(f"Initramfs generated -> {file_name}. Final size: {total_size} bytes.")
    p = process([binary_path, file_name])
    print(p.recvall().decode(errors="ignore"))


if __name__ == "__main__":
    build_payload()

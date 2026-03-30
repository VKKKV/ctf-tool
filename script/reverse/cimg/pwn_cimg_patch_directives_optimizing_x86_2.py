"""cIMG exploit: optimized x86 directive patching (variant 2)."""
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
            # 直接用索引取值，KISS 原则
            r, g, b, c = chunk[7], chunk[11], chunk[15], chunk[19]
            pixels.append((r, g, b, c))
        except IndexError:
            pass
    return pixels


def build_payload():
    binary_path = "/challenge/cimg"
    num_pixels = 1824

    pixels = extract_pixels_from_elf(binary_path, num_pixels)
    if len(pixels) != num_pixels:
        log.error("Failed to extract full image from binary. RTFM.")
        return

    best_size = float("inf")
    best_payload = b""
    best_w, best_h = 0, 0

    log.info("Initiating Arch-level topological brute-force...")

    # 遍历所有合法的长宽组合 (必须小于 256 因为是 uint8_t)
    for w in range(1, 256):
        if num_pixels % w != 0:
            continue
        h = num_pixels // w
        if h > 255:
            continue

        # 提取在这个特定拓扑结构下的所有非背景像素坐标
        boxes = []
        for i in range(num_pixels):
            # 过滤掉所有的空格和换行
            if pixels[i][3] not in (32, 10):
                x = i % w
                y = i // w
                boxes.append([x, y, x, y])

        # O(N^3) Agglomerative Clustering (自底向上合并区块)
        while True:
            best_saving = 0
            best_pair = None
            n = len(boxes)

            for i in range(n):
                for j in range(i + 1, n):
                    b1, b2 = boxes[i], boxes[j]
                    c1 = 6 + 4 * (b1[2] - b1[0] + 1) * (b1[3] - b1[1] + 1)
                    c2 = 6 + 4 * (b2[2] - b2[0] + 1) * (b2[3] - b2[1] + 1)

                    min_x, min_y = min(b1[0], b2[0]), min(b1[1], b2[1])
                    max_x, max_y = max(b1[2], b2[2]), max(b1[3], b2[3])

                    cm = 6 + 4 * (max_x - min_x + 1) * (max_y - min_y + 1)
                    saving = c1 + c2 - cm
                    if saving > best_saving:
                        best_saving = saving
                        best_pair = (i, j)

            if best_saving > 0:
                assert best_pair is not None, "Agglomerative Clustering failed"
                i, j = best_pair
                b1, b2 = boxes[i], boxes[j]
                merged = [
                    min(b1[0], b2[0]),
                    min(b1[1], b2[1]),
                    max(b1[2], b2[2]),
                    max(b1[3], b2[3]),
                ]
                # 注意：从后往前 pop 防止索引越界
                boxes.pop(j)
                boxes.pop(i)
                boxes.append(merged)
            else:
                break

        # 组装这个拓扑下的 Payload 并计算体积
        directives_payload = bytearray()
        SUB_BLOCK_OPCODE = 52965

        for b in boxes:
            bx, by = b[0], b[1]
            bw, bh = b[2] - b[0] + 1, b[3] - b[1] + 1

            directives_payload += struct.pack("<H", SUB_BLOCK_OPCODE)
            directives_payload += struct.pack("<BBBB", bx, by, bw, bh)

            for dy in range(bh):
                for dx in range(bw):
                    p = pixels[(by + dy) * w + bx + dx]
                    directives_payload += struct.pack("<BBBB", p[0], p[1], p[2], p[3])

        total_size = len(directives_payload) + 12

        if total_size < best_size:
            best_size = total_size
            best_w, best_h = w, h

            magic = b"cIMG"
            version = 3
            file_header = struct.pack("<4sHBBI", magic, version, w, h, len(boxes))

            best_payload = file_header + directives_payload

    log.success(
        f"Optimal Topology found: {best_w}x{best_h}. Payload size collapsed to {best_size} bytes!"
    )

    if best_size > 1337:
        log.error("Still exceeded 1337 limit. Time to debug the kernel source.")
        return

    file_name = "payload.cimg"
    with open(file_name, "wb") as f:
        f.write(best_payload)

    p = process([binary_path, file_name])
    print(p.recvall().decode(errors="ignore"))


if __name__ == "__main__":
    build_payload()

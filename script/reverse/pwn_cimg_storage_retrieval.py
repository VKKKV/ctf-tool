"""cIMG exploit: extract stored sprite data from ELF, replay as payload."""
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
            pixels.append((0, 0, 0, 32))
    return pixels


def build_arch_payload():
    binary_path = "/challenge/cimg"
    width = 76
    height = 24
    num_pixels = width * height

    log.info("Fetching raw pixel data from upstream...")
    pixels = extract_pixels_from_elf(binary_path, num_pixels)

    fg_pixels = []
    for y in range(height):
        for x in range(width):
            p = pixels[y * width + x]
            if p[3] not in (32, 10):
                fg_pixels.append(
                    {"x": x, "y": y, "r": p[0], "g": p[1], "b": p[2], "c": p[3]}
                )

    memo = {}

    def solve(min_x, max_x, min_y, max_y):
        state = (min_x, max_x, min_y, max_y)
        if state in memo:
            return memo[state]

        subset = [
            p
            for p in fg_pixels
            if min_x <= p["x"] <= max_x and min_y <= p["y"] <= max_y
        ]
        if not subset:
            return 0, []

        bx = min(p["x"] for p in subset)
        by = min(p["y"] for p in subset)
        b_w = max(p["x"] for p in subset) - bx + 1
        b_h = max(p["y"] for p in subset) - by + 1

        colors = set((p["r"], p["g"], p["b"]) for p in subset)

        # 12 = 5 字节 (handle_3 注册头部) + 7 字节 (handle_4 渲染头部)
        best_cost = 12 + b_w * b_h if len(colors) == 1 else float("inf")
        best_blocks = (
            [
                {
                    "x": bx,
                    "y": by,
                    "w": b_w,
                    "h": b_h,
                    "r": subset[0]["r"],
                    "g": subset[0]["g"],
                    "b": subset[0]["b"],
                    "subset": subset,
                }
            ]
            if len(colors) == 1
            else []
        )

        xs = sorted(list(set(p["x"] for p in subset)))
        for split_x in xs[1:]:
            c1, blks1 = solve(bx, split_x - 1, by, by + b_h - 1)
            c2, blks2 = solve(split_x, bx + b_w - 1, by, by + b_h - 1)
            if c1 + c2 < best_cost:
                best_cost = c1 + c2
                best_blocks = blks1 + blks2

        ys = sorted(list(set(p["y"] for p in subset)))
        for split_y in ys[1:]:
            c1, blks1 = solve(bx, bx + b_w - 1, by, split_y - 1)
            c2, blks2 = solve(bx, bx + b_w - 1, split_y, by + b_h - 1)
            if c1 + c2 < best_cost:
                best_cost = c1 + c2
                best_blocks = blks1 + blks2

        memo[state] = (best_cost, best_blocks)
        return best_cost, best_blocks

    log.info("Resolving dependencies and optimizing 2D bounding boxes (BSP DP)...")
    _, blocks = solve(0, width - 1, 0, height - 1)
    log.success(f"Reduced to {len(blocks)} highly optimized 2D blocks.")

    sprites = {}
    renders = []

    for blk in blocks:
        text = bytearray()
        for y in range(blk["h"]):
            for x in range(blk["w"]):
                found = False
                for p in blk["subset"]:
                    if p["x"] == blk["x"] + x and p["y"] == blk["y"] + y:
                        text.append(p["c"])
                        found = True
                        break
                if not found:
                    text.append(32)  # 使用空格填补空隙

        sp_key = (bytes(text), blk["w"], blk["h"])
        if sp_key not in sprites:
            sprites[sp_key] = len(sprites)

        renders.append(
            {
                "id": sprites[sp_key],
                "x": blk["x"],
                "y": blk["y"],
                "r": blk["r"],
                "g": blk["g"],
                "b": blk["b"],
            }
        )

    payload = bytearray()
    num_directives = len(sprites) + len(renders)
    payload += struct.pack("<4sHBBI", b"cIMG", 3, width, height, num_directives)

    for (text, bw, bh), sp_id in sprites.items():
        payload += struct.pack("<HBBB", 3, sp_id, bw, bh)
        payload += text

    for r in renders:
        payload += struct.pack(
            "<HBBBBBB", 4, r["id"], r["r"], r["g"], r["b"], r["x"], r["y"]
        )

    total_size = len(payload)
    if total_size > 400:
        log.error(f"Still bloated... ({total_size} bytes)")
        return

    log.success(
        f"Final Size: {total_size} bytes."
    )

    file_name = "payload.cimg"
    with open(file_name, "wb") as f:
        f.write(payload)

    try:
        p = process([binary_path, file_name])
        print(p.recvall(timeout=2).decode(errors="ignore"))
    except Exception:
        log.warning("Could not execute binary.")


if __name__ == "__main__":
    build_arch_payload()

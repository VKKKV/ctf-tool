"""cIMG exploit: read desired_output from ELF, craft sprite-based payload."""
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
            elif p[3] == 10:
                # Arch Way Hack: 换行符的颜色无所谓，全部刷成白色
                # 这样所有换行符就能组合成一个完美的 1x24 纯色垂直矩阵！
                fg_pixels.append(
                    {"x": x, "y": y, "r": 255, "g": 255, "b": 255, "c": 10}
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

        best_cost = float("inf")
        best_blocks = []

        # 只要区域内颜色单一，就可以作为一个 Render Directive
        if len(colors) == 1:
            chars = set(p["c"] for p in subset)
            # 检查是否是完美的“纯色单一字符”矩阵（例如连串的 '-' 或 '|' 或 '\n'）
            is_solid = len(subset) == b_w * b_h and len(chars) == 1
            if is_solid:
                best_cost = 17  # 5(注册1x1) + 1(数据) + 11(渲染并Tiling)
                best_blocks = [
                    {
                        "type": "solid",
                        "x": bx,
                        "y": by,
                        "w": b_w,
                        "h": b_h,
                        "r": subset[0]["r"],
                        "g": subset[0]["g"],
                        "b": subset[0]["b"],
                        "c": subset[0]["c"],
                        "subset": subset,
                    }
                ]
            else:
                best_cost = 16 + b_w * b_h  # 5(注册) + w*h(数据) + 11(镂空渲染)
                best_blocks = [
                    {
                        "type": "transparent",
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

        # 递归寻找最优切割
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

    log.info("Optimizing via 2D BSP with hardware Tiling and Chroma Key...")
    _, blocks = solve(0, width - 1, 0, height - 1)

    sprites = {}
    renders = []

    for blk in blocks:
        if blk["type"] == "solid":
            text = bytes([blk["c"]])
            bw, bh = 1, 1
            rx, ry = blk["w"], blk["h"]  # 启用 Tiling!
            trans = 0
        else:
            text_arr = bytearray()
            for y in range(blk["h"]):
                for x in range(blk["w"]):
                    found = False
                    for p in blk["subset"]:
                        if p["x"] == blk["x"] + x and p["y"] == blk["y"] + y:
                            text_arr.append(p["c"])
                            found = True
                            break
                    if not found:
                        text_arr.append(32)  # 空格占位
            text = bytes(text_arr)
            bw, bh = blk["w"], blk["h"]
            rx, ry = 1, 1
            trans = 32  # 启用 Chroma Key 透明度!

        sp_key = (text, bw, bh)
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
                "rx": rx,
                "ry": ry,
                "trans": trans,
            }
        )

    payload = bytearray()
    num_directives = len(sprites) + len(renders)

    # 写入 Version 4 的 Header
    payload += struct.pack("<4sHBBI", b"cIMG", 4, width, height, num_directives)

    # 指令 3：极简注册
    for (text, bw, bh), sp_id in sprites.items():
        payload += struct.pack("<HBBB", 3, sp_id, bw, bh)
        payload += text

    # 指令 4：11字节高级渲染
    for r in renders:
        payload += struct.pack(
            "<HBBBBBBBBB",
            4,
            r["id"],
            r["r"],
            r["g"],
            r["b"],
            r["x"],
            r["y"],
            r["rx"],
            r["ry"],
            r["trans"],
        )

    total_size = len(payload)
    if total_size > 285:
        log.error(f"System still bloated... ({total_size} bytes)")
        return

    log.success(f"Arch Way achieved. Zero Bloatware. Final Size: {total_size} bytes.")

    file_name = "payload.cimg"
    with open(file_name, "wb") as f:
        f.write(payload)

    try:
        p = process([binary_path, file_name])
        print(p.recvall(timeout=2).decode(errors="ignore"))
    except Exception:
        log.warning("Execute the payload on the target remote!")


if __name__ == "__main__":
    build_arch_payload()

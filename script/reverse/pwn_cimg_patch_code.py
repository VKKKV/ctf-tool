"""cIMG exploit: brute-force flag by patching binary code at runtime."""
import struct
import subprocess

from pwn import *


def solve(known_flag):
    try:
        p = process(
            ["/challenge/quest.py"],
            stdin=process.PTY,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
    except Exception as e:
        return known_flag

    try:
        p.recvn(12)  # 魔数
    except EOFError:
        return known_flag

    state = {
        "px": -1,
        "py": -1,
        "hx": -1,
        "hy": -1,
        "bx": -1,
        "by": -1,
        "frame_flag": "",
    }

    def parse_frame():
        state["px"] = state["bx"] = state["hx"] = -1
        frame_chars = ""
        saw_player = False

        while True:
            try:
                # 超时阻断，防止卡在输入缓冲区死锁
                if not p.can_recv(timeout=0.2):
                    return "TIMEOUT"

                op_bytes = p.recvn(2)
                if not op_bytes:
                    return False
                op = struct.unpack("<H", op_bytes)[0]
            except EOFError:
                return False

            if op == 7:  # RENDER_FRAME
                p.recvn(70 * 20 * 4)
            elif op == 6:  # RENDER_PATCH
                px, py, pw, ph = struct.unpack("<BBBB", p.recvn(4))
                pixels = p.recvn(pw * ph * 4)
                if pw == 1 and ph == 1:
                    # 获取 RGB 和 字符
                    r_col, g_col, b_col, c = pixels[0], pixels[1], pixels[2], pixels[3]
                    if c == ord("?"):
                        state["hx"], state["hy"] = px, py
                    elif c == ord("B") and r_col == 0xff and g_col == 0xc6 and b_col == 0x27:
                        # 只有黄色 (255, 198, 39) 的 B 才是炸弹， Flag may be B
                        state["bx"], state["by"] = px, py
                    elif chr(c) not in (" ", "!", "#"):
                        frame_chars += chr(c)
            elif op == 5:  # CREATE_SPRITE
                s_id, sw, sh = struct.unpack("<BBB", p.recvn(3))
                p.recvn(sw * sh)
            elif op == 4:  # RENDER_SPRITE
                num, r, g, b, px, py, tx, ty, tc = struct.unpack(
                    "<BBBBBBBBB", p.recvn(9)
                )
                if num == 0:
                    state["px"], state["py"] = px, py
                    saw_player = True
            elif op == 2:  # FLUSH (当前帧渲染完毕)
                p.recvn(1)
                if saw_player or "pwn.college" in frame_chars:
                    state["frame_flag"] = frame_chars
                return True
            elif op == 1:  # SLEEP
                p.recvn(4)
            else:
                return False
    def get_best_move(px, py, hx, hy, bx, by):
        """BFS 最短路径寻路"""
        queue = [(px, py, [])]
        visited = set([(px, py)])
        while queue:
            cx, cy, path = queue.pop(0)

            # 3x2 bounding box
            if hx in (cx, cx + 1, cx + 2) and hy in (cy, cy + 1):
                return path[0] if path else "l"

            for key, dx, dy in [("w", 0, -1), ("s", 0, 1), ("a", -1, 0), ("d", 1, 0)]:
                # Toroidal Map Wrapping
                nx, ny = (cx + dx) % 70, (cy + dy) % 20
                # boom here
                if not (bx in (nx, nx + 1, nx + 2) and by in (ny, ny + 1)):
                    if (nx, ny) not in visited:
                        visited.add((nx, ny))
                        queue.append((nx, ny, path + [key]))
        return "SOFTLOCK"

    while True:
        res = parse_frame()

        if res == "TIMEOUT":
            p.send(b" ")
            continue

        if not res:
            p.close()
            break

        # 增量比对：只在提取进度超越已知记录时才打印
        if state["frame_flag"] and len(state["frame_flag"]) > len(known_flag):
            known_flag = state["frame_flag"]
            print(f"[+] Extracted so far: {known_flag}")
            if known_flag.endswith("}"):
                p.close()
                return known_flag

        if state["px"] != -1 and state["bx"] != -1 and state["hx"] != -1:
            move = get_best_move(
                state["px"],
                state["py"],
                state["hx"],
                state["hy"],
                state["bx"],
                state["by"],
            )
            if move == "SOFTLOCK":
                print(
                    f"[*] Soft-lock detected at Target ({state['hx']:02d},{state['hy']:02d}). "
                )
                p.close()
                return known_flag
            p.send(move.encode())
    return known_flag


if __name__ == "__main__":
    print("START")
    current_flag = ""
    while True:
        current_flag = solve(current_flag)


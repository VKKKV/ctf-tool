"""Generic challenge solver: run binary and extract flag via regex."""
import re

from pwn import *
from pwn import context, process

context.log_level = "error"


def solve():
    p = process("/challenge/run")

    p.recvuntil(b"Levels (first is highest aka more sensitive):\n")

    # 动态解析 Level 权重 (先读到的权重最高)
    level_map = {}
    current_weight = 100

    while True:
        line = p.recvline().decode().strip()
        if "Categories:" in line or line.startswith("Q 1"):
            break
        if line:
            level_map[line] = current_weight
            current_weight -= 1

    for i in range(64):
        p.recvuntil(b"Q ")
        question = p.recvline().decode().strip()

        # 匹配: level [S] and categories [{...}] [read/write] an Object with level [C] and categories [{...}]?
        match = re.search(
            r"level (.*?) and categories \{(.*?)\} (read|write) an Object with level (.*?) and categories \{(.*?)\}\?",
            question,
        )

        assert match is not None, f"Regex failed to match the question: {question}"

        sub_lvl = match.group(1)
        sub_cats_str = match.group(2)
        action = match.group(3)
        obj_lvl = match.group(4)
        obj_cats_str = match.group(5)

        # 转换为 Python Set
        sub_cats = set(filter(None, [x.strip() for x in sub_cats_str.split(",")]))
        obj_cats = set(filter(None, [x.strip() for x in obj_cats_str.split(",")]))

        sub_weight = level_map[sub_lvl]
        obj_weight = level_map[obj_lvl]

        is_allowed = False

        if action == "read":
            if sub_weight >= obj_weight and sub_cats.issuperset(obj_cats):
                is_allowed = True
        elif action == "write":
            if sub_weight <= obj_weight and sub_cats.issubset(obj_cats):
                is_allowed = True

        if is_allowed:
            p.sendline(b"yes")
        else:
            p.sendline(b"no")

        p.recvline()

    print("[+] MAC Engine bypassed successfully.")
    p.interactive()


if __name__ == "__main__":
    solve()

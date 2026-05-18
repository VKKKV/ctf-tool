#!/usr/bin/env python3
import itertools


def solve_24(nums):
    if len(nums) != 4:
        return "RTFM: 请输入4个数字"

    ops = ["+", "-", "*", "/"]
    # 4个数字的5种AST（抽象语法树）形态，完美覆盖所有括号优先级组合
    shapes = [
        "(({0} {4} {1}) {5} {2}) {6} {3}",
        "({0} {4} ({1} {5} {2})) {6} {3}",
        "{0} {4} (({1} {5} {2}) {6} {3})",
        "{0} {4} ({1} {5} ({2} {6} {3}))",
        "({0} {4} {1}) {5} ({2} {6} {3})",
    ]

    results = set()
    for n in itertools.permutations(nums):
        for op in itertools.product(ops, repeat=3):
            for shape in shapes:
                expr = shape.format(n[0], n[1], n[2], n[3], op[0], op[1], op[2])
                try:
                    # 使用 eval 快速计算，捕获除以零的异常
                    val = eval(expr)
                    # 浮点数精度处理
                    if abs(val - 24.0) < 1e-6:
                        results.add(expr)
                except ZeroDivisionError:
                    pass

    if not results:
        return "无解 (Unsolvable)。放弃吧，你的直觉在机器穷举面前一文不值。"

    return "\n".join(results)


if __name__ == "__main__":
    # 测试你的 2, 5, 7, 8
    target_nums = [2, 5, 7, 8]
    print(f"Target: {target_nums}")
    print("-" * 20)
    print(solve_24(target_nums))

    print("\nTarget: [3, 3, 8, 8]")
    print("-" * 20)
    print(solve_24([3, 3, 8, 8]))  # 你可以试试这个经典的通过分数解决的难题

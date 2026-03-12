import r2pipe


def area_logic_wipe(file_path, start_addr, end_addr):
    print(f"[*] I use Arch btw. 启动区间清洗模式: {start_addr} -> {end_addr}")

    # 以读写模式打开
    try:
        r = r2pipe.open(file_path, flags=["-w"])
        # 预先分析，获取更准确的 opcode 信息
        r.cmd("aa")
    except Exception as e:
        print(f"[!] 无法接管文件: {e}")
        return

    # 计算区间大小并反汇编
    # 我们使用 pDj 获取指定字节长度的反汇编 JSON
    range_size = int(end_addr, 16) - int(start_addr, 16)
    if range_size <= 0:
        print("[!] 区间设置错误，Start 必须小于 End。")
        return

    print(f"[*] 正在分析区间内的 {range_size} 字节...")
    instructions = r.cmdj(f"pDj {range_size} @ {start_addr}")

    patched_count = 0

    for instr in instructions:
        # 获取指令的基本信息
        offset = instr.get("offset")
        opcode = instr.get("opcode", "").lower()
        size = instr.get("size", 0)

        # 匹配所有类型的 Jump Not Zero / Jump Not Equal
        if "jnz" in opcode or "jne" in opcode or "je" in opcode:
            print(f"[!] 发现跳转漏洞: {hex(offset)} -> `{opcode}` ({size} bytes)")

            # 构造对应长度的 NOP 序列
            nop_hex = "90" * size
            r.cmd(f"wx {nop_hex} @ {offset}")

            patched_count += 1
            print(f"    [+] 已抹除: {hex(offset)}")

    print(f"\n[*] 清洗完成。共处理 {patched_count} 处逻辑跳转。")
    r.quit()


if __name__ == "__main__":
    # 配置你的战场参数
    TARGET_FILE = "flag_errata.exe"

    # 你可以从 r2 中通过 `V` 模式观察逻辑块的起始和结束
    START_RANGE = "0x403100"
    END_RANGE = "0x410263"

    area_logic_wipe(TARGET_FILE, START_RANGE, END_RANGE)

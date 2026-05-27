#!/bin/bash
# 快速编译 ld-preload-hooks.so 的各种配置
# 用法: ./compile-hook.sh [模块名...]
#   ./compile-hook.sh                  # 默认全部启用
#   ./compile-hook.sh strcmp ptrace    # 只启用指定模块
#   ./compile-hook.sh all              # = -DENABLE_ALL

set -e

DIR="$(cd "$(dirname "$0")" && pwd)"
SRC="$DIR/ld-preload-hooks.c"
OUT="$DIR/ld-preload-hooks.so"

if [ $# -eq 0 ] || [ "$1" = "all" ]; then
    FLAGS="-DENABLE_ALL"
else
    FLAGS=""
    for mod in "$@"; do
        FLAGS="$FLAGS -DENABLE_$(echo "$mod" | tr '[:lower:]' '[:upper:]')"
    done
fi

echo "[-] Compiling: $FLAGS"
gcc -Wall -shared -fPIC -ldl -o "$OUT" "$SRC" $FLAGS 2>&1 \
    | grep -v "nonnull argument.*compared to NULL" || true
echo "[+] Output: $OUT"
echo "[+] Usage: LD_PRELOAD=$OUT ./target"

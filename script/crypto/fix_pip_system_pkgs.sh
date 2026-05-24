#!/bin/bash
# 清理 pip 安装的系统 Python 包，替换为 pacman/paru 版本
# 用于修复混合 pip+pacman 环境导致的冲突
# 用法: ./fix_pip_system_pkgs.sh [--dry-run] [--restore]

set -euo pipefail

DRY_RUN=false
RESTORE=false
BACKUP_FILE="/tmp/pip-system-pkgs-backup-$(date +%Y%m%d).log"

while [[ $# -gt 0 ]]; do
    case "$1" in
        --dry-run) DRY_RUN=true; shift ;;
        --restore) RESTORE=true; shift ;;
        *) echo "Usage: $0 [--dry-run] [--restore]"; exit 1 ;;
    esac
done

if $RESTORE; then
    echo "[*] 从 $BACKUP_FILE 恢复..."
    if [[ -f "$BACKUP_FILE" ]]; then
        while IFS= read -r pkg; do
            echo "  pip install $pkg"
        done < "$BACKUP_FILE"
    else
        echo "  ! 无备份文件，跳过恢复"
    fi
    exit 0
fi

echo "[*] 扫描 pip 安装的包..."
PIP_PKGS=$(pip list --format=columns 2>/dev/null | tail -n +3 | head -n -1 | awk '{print $1}')

# 规范化包名: _ → -, 大写 → 小写
normalize() {
    echo "$1" | tr '[:upper:]' '[:lower:]' | tr '_' '-'
}

REMOVED=()
for pkg in $PIP_PKGS; do
    arch_pkg="python-$(normalize "$pkg")"
    if pacman -Si "$arch_pkg" &>/dev/null; then
        echo "  -> $pkg (arch: $arch_pkg) available in pacman"
        REMOVED+=("$pkg")
    fi
done

if [[ ${#REMOVED[@]} -eq 0 ]]; then
    echo "[*] 没有需要清理的包"
    exit 0
fi

echo
echo "[*] 发现 ${#REMOVED[@]} 个 pip 包有 pacman 版本"
for pkg in "${REMOVED[@]}"; do
    echo "    - $pkg"
done

if $DRY_RUN; then
    echo "[*] --dry-run 模式，不执行操作"
    exit 0
fi

echo "[*] 备份已删除包列表到 $BACKUP_FILE"
printf '%s\n' "${REMOVED[@]}" > "$BACKUP_FILE"

echo "[*] 卸载 pip 包..."
pip uninstall -y "${REMOVED[@]}" 2>/dev/null || true

echo
echo "[*] 安装对应的 pacman 包..."
for pkg in "${REMOVED[@]}"; do
    arch_pkg="python-$(normalize "$pkg")"
    echo "  -> sudo pacman -S $arch_pkg"
done
echo
echo "[!] 上面的 pacman 包需要手动运行 sudo pacman -S ... 安装"
echo "[*] 备份文件: $BACKUP_FILE"

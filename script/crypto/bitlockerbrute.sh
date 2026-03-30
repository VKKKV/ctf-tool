#!/usr/bin/env bash

IMG_FILE="encrypted_usb.dd"
MNT_DIR="/mnt/bitlocker_img"
USB_DIR="/mnt/unlocked_usb"
KEYS_FILE="recovery_keys_dump.txt"

if [[ $EUID -ne 0 ]]; then
   echo "[-] Error: This script must be run as root. Stop spamming sudo in loops." 
   exit 1
fi

mkdir -p "$MNT_DIR" "$USB_DIR"

while IFS= read -r key; do
    if dislocker -V "$IMG_FILE" -p"$key" -- "$MNT_DIR" 2>/dev/null; then
        echo -e "\n[+] Recovery Key Found: $key"
        break
    fi
done < "$KEYS_FILE"

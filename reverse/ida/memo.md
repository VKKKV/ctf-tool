```bash
chmod a+x ./ida-pro_92_x64linux.run
./ida-pro_92_x64linux.run   安装软件，并指定安装目录，

uv venv
 
idapyswitch --force-path /path/lib/libpython3.13.so
 
cp keygen.py /path/ida-pro-9.2/   移动到安装目录
python keygen.py --oneshot
 
vim .local/bin/ida9

#!/bin/bash
export IDA_DIR="$HOME/ctf/ida-pro-9.2"
export PYTHONPATH="$IDA_DIR/.venv/lib/python3.13/site-packages"
exec "$IDA_DIR/ida" "$@"

vim .local/share/applications/ida9.desktop

[Desktop Entry]
Version=1.0
Type=Application
Name=IDA Pro 9.2
Comment=The Interactive Disassembler
# 直接调用我们的 wrapper
Exec=/home/kita/.local/bin/ida9 %f
# 图标路径要对
Icon=/home/kita/ctf/ida-pro-9.2/appico.png
Terminal=false
Categories=Development;Debugger;
StartupNotify=true
MimeType=application/x-executable;application/x-sharedlib;application/x-object;
```

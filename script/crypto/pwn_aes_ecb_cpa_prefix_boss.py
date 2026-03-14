import string

import requests
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
from Crypto.Util.Padding import pad
from pwn import *
from pwn import b64d, b64e, context, enhex, log, process, remote, unhex, xor

# 16 bytes 128 bits a time
# PKCS#7 default pad()

context.log_level = "info"

charset = string.printable.strip()

URL = "http://challenge.localhost"
CHARSET = string.printable.strip() + "}"

log.info("Start")

result = b""

block_size = 16

# b"A|flag{arch_linux_is_the_best_distro}"


def send_data(data):
    r = requests.post(URL, data={"content": data + "A"})
    if r.status_code != 200:
        exit()


def cleanup():
    r = requests.post(URL + "/reset")
    if r.status_code != 200:
        exit()


def send_part_of_flag(data):
    send_data(data.decode("latin1"))
    # <b>Encrypted backup:</b><pre>{b64encode(ct).decode()}</pre>
    r = requests.get(URL)
    a = r.text.split("<b>Encrypted backup:</b><pre>")[1].split("</pre>")[0]
    b = b64d(a)
    cleanup()
    return b


for i in range(1, 60):
    block_idx = (i - 1) // block_size
    pad_len = (block_size - i) % block_size
    padding = b"A" * pad_len

    ct = send_part_of_flag(padding)

    target_block = ct[block_idx * 16 : (block_idx + 1) * 16]

    for c in charset:
        c = c.encode()
        ct2 = send_part_of_flag(padding + result + c)
        guess_block = ct2[block_idx * 16 : (block_idx + 1) * 16]
        if guess_block == target_block:
            log.success(f"Found: {c} at {i}")
            result = result + c
            break

print(result)

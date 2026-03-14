import os

from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
from Crypto.Util.Padding import pad, unpad
from pwn import *
from pwn import context, enhex, log, process, unhex, xor

# CBC mode
# cipher block chaining
# IV Initialization Vector
# POA padding oracle attack


def check_padding(p_worker, iv_test, cipher_block):
    payload = (iv_test + cipher_block).hex()
    p_worker.sendline(f"TASK: {payload}".encode())
    response = p_worker.recvline().decode()
    return "Error" not in response


log.info("Start")

p_worker = process(["/challenge/worker"])

target_message = b"please give me the flag, kind worker process!"
target_message = pad(target_message, 16)
message_blocks = [target_message[i : i + 16] for i in range(0, len(target_message), 16)]

forged_ciphertext = [os.urandom(16)]

# 逆向遍历目标明文块
for block_idx, p_block in enumerate(reversed(message_blocks)):
    log.info(
        f"Forging block {len(message_blocks) - block_idx} / {len(message_blocks)}..."
    )
    current_cipher_block = forged_ciphertext[0]
    intermediate_value = bytearray(16)

    # 爆破 16 个 byte
    for pad_val in range(1, 17):
        idx = 16 - pad_val
        found = False

        for guess in range(256):
            test_iv = bytearray(16)
            # 填充已知的中间值，构造所需的 padding
            for i in range(idx + 1, 16):
                test_iv[i] = intermediate_value[i] ^ pad_val

            test_iv[idx] = guess

            if check_padding(p_worker, bytes(test_iv), current_cipher_block):
                # 处理 padding=1 时的 false positive
                # 如果你爆破 `idx = 15` 时，原密文的解密结果恰好是 `0x02 0x02`，就会因为误判 `0x01` 成功。
                if pad_val == 1:
                    test_iv[idx - 1] ^= 1
                    if not check_padding(
                        p_worker, bytes(test_iv), current_cipher_block
                    ):
                        continue

                intermediate_value[idx] = guess ^ pad_val
                found = True
                break

        if not found:
            log.error("Fail")
            exit(1)

    prev_cipher_block = xor(bytes(intermediate_value), p_block)
    forged_ciphertext.insert(0, prev_cipher_block)

iv = forged_ciphertext[0]
final_ciphertext = b"".join(forged_ciphertext[1:])
final_payload = (iv + final_ciphertext).hex()

log.success("Payload forged successfully. Sending to worker...")
p_worker.sendline(f"TASK: {final_payload}".encode())

print(p_worker.recvall(timeout=2).decode())

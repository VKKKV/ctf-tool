from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
from Crypto.Util.Padding import pad, unpad
from pwn import *
from pwn import context, enhex, log, process, unhex, xor

# CBC mode
# cipher block chaining
# IV Initialization Vector
# POA padding oracle attack


def get_encrypted_password():
    p = process(["/challenge/dispatcher", "pw"])
    p.recvuntil(b"TASK: ")
    res = unhex(p.recvline().strip())
    p.close()
    return res


def check_padding(p_worker, iv_test, cipher_block):
    payload = (iv_test + cipher_block).hex()
    p_worker.sendline(f"TASK: {payload}".encode())
    response = p_worker.recvline().decode()
    return "Error" not in response


log.info("Start")

target_data = get_encrypted_password()
blocks = [target_data[i : i + 16] for i in range(0, len(target_data), 16)]
p_worker = process(["/challenge/worker"], stdin=process.PTY, stdout=process.PTY)
p_worker.recvline()

recovered_plaintext = b""

for block_idx in range(1, len(blocks)):
    current_cipher_block = blocks[block_idx]
    original_prev_block = blocks[block_idx - 1]

    intermediate_value = bytearray(16)

    # 从块的最后一个字节向前爆破 (15 down to 0)
    for pad_val in range(1, 17):
        idx = 16 - pad_val

        for guess in range(256):
            # 构造用于测试的伪造前一块 (C'_{n-1})
            test_iv = bytearray(16)

            # 填充已经爆破出的中间值字节，使其异或后等于当前 pad_val
            for i in range(idx + 1, 16):
                test_iv[i] = intermediate_value[i] ^ pad_val

            # 将我们当前的猜测放入 target 字节
            test_iv[idx] = guess

            if check_padding(p_worker, bytes(test_iv), current_cipher_block):
                # 找到了正确的 guess，由于我们可能有 0x01 的伪正例，严谨起见需要进一步校验（此处从简）
                intermediate_value[idx] = guess ^ pad_val
                print(f"[+] Found byte {idx}: {hex(intermediate_value[idx])}")
                break

    # P_n = Intermediate_n \oplus C_{n-1}
    decrypted_block = xor(bytes(intermediate_value), original_prev_block)
    recovered_plaintext += decrypted_block
    print(f"[*] Decrypted block {block_idx}: {decrypted_block}")

# 去除 PKCS#7 padding
final_password = unpad(recovered_plaintext, 16).decode("latin1")
print(f"\n[!] Extracted Password: {final_password}")

p_redeem = process(["/challenge/redeem"])
p_redeem.recvuntil(b"Password? ")
p_redeem.sendline(final_password.encode())
print(p_redeem.recvall().decode())

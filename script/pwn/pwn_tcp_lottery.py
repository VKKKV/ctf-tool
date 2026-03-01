#!/usr/bin/env python3
import random
import time

from pwn import context, remote

# Server configuration
HOST = "13721472f3c35e88.247ctf.com"
PORT = 50316

# Exploit configuration
TIME_OFFSET_RANGE = range(0, 10)  # Try offsets from 0 to 9 seconds ahead
FLAG_SUBSTRING = "247"  # Success indicator in server response

# Suppress non-essential pwnlib logs
context.log_level = "error"


def generate_legacy_random_seed(timestamp: int) -> str:
    rng = random.Random()
    rng.seed(timestamp)
    return str(rng.random())


def attempt_exploit(host: str, port: int, time_offset: int) -> bool:
    current_time = int(time.time())
    target_time = current_time + time_offset
    predicted_random = generate_legacy_random_seed(target_time)

    print(
        f"[*] Trying offset +{time_offset}s | Target time: {target_time} | Payload: {predicted_random}"
    )

    try:
        conn = remote(host, port)

        # Receive initial prompt/banner
        conn.recvline()

        # Send predicted random value
        conn.sendline(predicted_random.encode())

        # Receive full response
        response = conn.recvall().decode()

        if FLAG_SUBSTRING in response:
            print(f"[+] SUCCESS! Server response:\n{response.strip()}")
            conn.interactive()
            return True
        else:
            print(f"[-] Failed: {response.strip()}")
            conn.close()
            return False

    except Exception as e:
        print(f"[!] Connection error: {e}")
        return False


def main():
    print(f"[*] Target: {HOST}:{PORT}")
    print(f"[*] Trying time offsets: {list(TIME_OFFSET_RANGE)}")
    print("-" * 60)

    for offset in TIME_OFFSET_RANGE:
        if attempt_exploit(HOST, PORT, offset):
            print("[*] Exploit completed successfully!")
            return

    print("[-] All attempts failed. Try increasing the offset range.")


if __name__ == "__main__":
    main()

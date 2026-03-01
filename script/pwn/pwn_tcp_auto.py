#!/usr/bin/env python3
import pwn

HOST = "7a3875d00fa5d462.247ctf.com"
PORT = 50337


def solve_challenge():
    conn = None
    try:
        conn = pwn.remote(HOST, PORT)

        for i in range(500):
            conn.recvuntil(b"answer to ")

            question_line = conn.recvline().decode().strip()

            expression = question_line.replace("?", "")

            result = int(eval(expression))

            conn.sendline(str(result).encode())

            pwn.log.info(f"Progress: [{i + 1}/500] Solved: {expression} = {result}")

        pwn.log.success("500 problems solved! Waiting for flag...")
        conn.interactive()

        # recvall will block until the connection is closed
        # flag = conn.recvall().decode()
        # print(f"\n[+] FLAG: {flag}")

    except Exception as e:
        pwn.log.error(f"An error occurred: {e}")

    finally:
        if conn:
            pwn.log.info("Connection closed.")
            conn.close()


if __name__ == "__main__":
    pwn.context.log_level = "info"
    pwn.tube.newline = b"\r\n"
    solve_challenge()

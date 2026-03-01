#!/usr/bin/env python3
import json
import zlib

from pwn import *
from pwn import context, log, remote, ssh, tube

"""
Pwn TCP Tool - A consolidated utility for CTF PWN challenges.
Optimized for readability and consistent pwntools usage.
"""

# Default Target Configuration
# tcp://35f9359cc67c7983.247ctf.com:50385
HOST = "35f9359cc67c7983.247ctf.com"
PORT = 50385
context.log_level = "info"
tube.newline = b"\r\n"


class PwnTool:
    """
    A lightweight wrapper for pwntools' remote and ssh functionalities.
    """

    def __init__(
        self,
        host: str = HOST,
        port: int = PORT,
    ):
        self.host = host
        self.port = port
        self.conn = self.connect()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def connect(self):
        """Establishes a remote connection."""
        try:
            self.conn = remote(self.host, self.port)
            return self.conn
        except Exception as e:
            log.error(f"Failed to connect to {self.host}:{self.port} -> {e}")

    def close(self):
        """Closes the connection gracefully."""
        if self.conn:
            self.conn.close()
            log.info("Connection closed.")

    def send_json(self, data: dict):
        """Encodes and sends a dictionary as a JSON line."""
        if self.conn:
            self.conn.sendline(json.dumps(data).encode())

    def recv_json(self):
        """Receives a line and decodes it as JSON."""
        if self.conn:
            return json.loads(self.conn.recvline().decode())

    @staticmethod
    def ssh_connect(host, port, user, password):
        """Helper for SSH-based pwn challenges."""
        try:
            shell = ssh(host=host, port=port, user=user, password=password)
            log.success(f"SSH Connected: {user}@{host}:{port}")
            return shell
        except Exception as e:
            log.error(f"SSH Connection failed: {e}")


def calc_custom_crc_hex(hex_data: str) -> str:
    """
    Calculates CRC32 of hex data and returns the hex representation
    of its decimal string (specific to this challenge logic).
    """
    data_bytes = bytes.fromhex(hex_data)
    crc_val = zlib.crc32(data_bytes)
    return str(crc_val).encode().hex()


def solve():
    """Main solver logic for the specific challenge."""
    sep = "00"
    counter = "31"
    # Commands 0-14 in a specific hex format
    commands = [f"3{hex(i)[2:]}" for i in range(15)]

    log.info(f"Starting brute-force with commands: {commands}")

    for cmd in commands:
        with PwnTool() as tool:
            conn = tool.conn
            # Receive Session ID
            session_id = conn.recvline(drop=True).decode(errors="replace")
            log.info(f"Session ID: {session_id}")

            # Construct payload: [SessionID][00][Counter][00][Command]
            base_hex = f"{session_id}{sep}{counter}{sep}{cmd}"
            crc_hex = calc_custom_crc_hex(base_hex)

            payload = f"{base_hex}{sep}{crc_hex}"
            log.debug(f"Payload: {payload}")

            conn.sendline(payload.encode())

            # Receive and process response
            raw_response = conn.recvall(timeout=3).decode(errors="replace")
            try:
                decoded_response = bytes.fromhex(raw_response).decode(errors="replace")
                log.info(f"Response: {decoded_response}")

                if "247CTF" in decoded_response:
                    log.success(f"Flag found: {decoded_response}")
                    return
            except ValueError:
                log.warning(f"Failed to decode hex response: {raw_response}")

            print("-" * 40)


if __name__ == "__main__":
    solve()

#!/usr/bin/env python3
"""
Simple TCP Client for CTF Socket Challenges
Allows interactive communication with a remote server.
"""

import socket
import sys

# --- Configuration ---
HOST = "101.132.242.241"
PORT = 33065
BUFFER_SIZE = 4096

def start_client():
    try:
        # Create socket and connect
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            print(f"[*] Connecting to {HOST}:{PORT}...")
            sock.connect((HOST, PORT))
            print("[+] Connected! Enter 'quit' to exit.\n")

            while True:
                # Get user input
                message = input(">>> ")
                if message.lower() in ["quit", "exit"]:
                    print("[*] Communication ended.")
                    break

                # Send data
                sock.sendall(message.encode("utf-8"))

                # Receive response
                data = sock.recv(BUFFER_SIZE)
                if not data:
                    print("[-] Connection closed by server.")
                    break
                
                print(f"[*] Server response: {data.decode('utf-8', errors='replace')}")

    except ConnectionRefusedError:
        print(f"[!] Error: Connection refused by {HOST}:{PORT}")
    except Exception as e:
        print(f"[!] Error: {e}")

if __name__ == "__main__":
    start_client()

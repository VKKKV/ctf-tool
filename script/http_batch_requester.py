#!/usr/bin/env python3
"""
Simple HTTP GET Requester
Appends lines from stdin to a base URL and prints the response.
"""

import requests
import sys

BASE_URL = "http://192.168.0.109/shehatesme"

def main():
    print(f"[*] Sending requests to {BASE_URL}...")
    
    for line in sys.stdin:
        path_suffix = line.strip()
        if not path_suffix:
            continue
            
        target = f"{BASE_URL}{path_suffix}"
        try:
            response = requests.get(target, timeout=5)
            # Print status and a preview of the response
            print(f"[{response.status_code}] {target}")
            print(response.text.strip())
            print("-" * 20)
        except requests.RequestException as e:
            print(f"[!] Error requesting {target}: {e}")

if __name__ == "__main__":
    main()

#!/usr/bin/env python3

import requests

BASE_URL = "https://9894a61910fb83f2.247ctf.com/calculator"


def main():
    print(f"[*] Sending requests to {BASE_URL}...")

    number_1 = 1
    number_2 = 0
    operation = "/"
    payload = f"?number_1={number_1}&number_2={number_2}&operation={operation}"
    target = f"{BASE_URL}{payload}"
    try:
        response = requests.get(target, timeout=5)
        print(f"[{response.status_code}] {target}")
        print(response.text.strip())
        print("-" * 20)
    except requests.RequestException as e:
        print(f"[!] Error requesting {target}: {e}")

if __name__ == "__main__":
    main()

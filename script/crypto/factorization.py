#!/usr/bin/env python3
import json
import sys
import urllib.error
import urllib.request


def query_factordb(number: str):
    url = f"http://factordb.com/api?query={number}"
    headers = {"User-Agent": "ArchLinux-PowerUser/1.0"}

    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read().decode("utf-8"))

            status = data.get("status", "Unknown")
            factors = data.get("factors", [])

            print(f"[*] Target : {number}")
            print(f"[*] Status : {status}")

            if factors:
                result = " * ".join([f"{base}^{exp}" for base, exp in factors])
                print(f"[*] Factors: {result}")
            else:
                print("[!] No factors returned.")

    except urllib.error.URLError as e:
        print(f"[!] Network Error: {e.reason}")
    except ValueError:
        print("[!] JSON parsing failed. Did FactorDB change their API?")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: ./fdb.py <number>")
        sys.exit(1)

    query_factordb(sys.argv[1])

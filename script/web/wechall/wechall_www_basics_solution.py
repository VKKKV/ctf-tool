#!/usr/bin/env python3
"""
WeChall Training: WWW-Basics Solution
======================================
Challenge: https://www.wechall.net/challenge/training/www/basic/index.php

Task:
- Run an HTTP server on your machine (publicly accessible)
- Serve file: <YOUR_IP>/Guest/Guest.html
- Content exactly: "My name is Guest and iChall." (28 bytes)
- WeChall's server will connect to YOUR IP to verify
"""

import http.server
import socketserver
import sys

PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 80

# Must be exactly 28 bytes - use -n when echoing!
CONTENT = b"My name is Guest and iChall."
CONTENT_LEN = len(CONTENT)
assert CONTENT_LEN == 28, f"Content must be 28 bytes, got {CONTENT_LEN}"

class Handler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        print(f"[*] Request: {self.path} from {self.client_address}")
        if self.path == '/Guest/Guest.html':
            self.send_response(200)
            self.send_header('Content-Type', 'text/html')
            self.send_header('Content-Length', str(CONTENT_LEN))
            self.end_headers()
            self.wfile.write(CONTENT)
            print(f"[+] Served: {CONTENT.decode()}")
        else:
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b"Not found")

if __name__ == '__main__':
    print(f"[*] Content: '{CONTENT.decode()}' ({CONTENT_LEN} bytes)")
    print(f"[*] Starting server on port {PORT}...")
    with socketserver.TCPServer(("", PORT), Handler) as httpd:
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n[*] Server stopped.")

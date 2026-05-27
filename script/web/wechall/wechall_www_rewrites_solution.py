#!/usr/bin/env python3
"""
WeChall Training: WWW-Rewrites Solution
========================================
Challenge: https://www.wechall.net/challenge/training/www/rewrite/index.php

Task:
- Run an HTTP server that handles dynamic URL patterns
- WeChall requests: /Guest/[0-9]+_mul_[0-9]+.html
- Respond with the multiplication result (as plain text)
- Example: /Guest/1000_mul_20.html -> respond "20000"
"""

import http.server
import socketserver
import re
import sys

PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 80

# Pattern: /Guest/<number>_mul_<number>.html
PATH_PATTERN = re.compile(r'^/Guest/(\d+)_mul_(\d+)\.html$')

class Handler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        print(f"[*] Request: {self.path} from {self.client_address}")
        match = PATH_PATTERN.match(self.path)
        if match:
            a, b = int(match.group(1)), int(match.group(2))
            result = str(a * b)
            print(f"[+] Computed: {a} * {b} = {result}")
            self.send_response(200)
            self.send_header('Content-Type', 'text/plain')
            self.send_header('Content-Length', str(len(result)))
            self.end_headers()
            self.wfile.write(result.encode())
        else:
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b"Not found")

if __name__ == '__main__':
    print(f"[*] Starting server on port {PORT}...")
    print(f"[*] Handles URLs like: /Guest/1000_mul_20.html -> 20000")
    with socketserver.TCPServer(("", PORT), Handler) as httpd:
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n[*] Server stopped.")

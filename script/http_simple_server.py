#!/usr/bin/env python3
"""
Quick HTTP File Server
Serves the current directory on a specified port.
"""

import http.server
import socketserver
import sys

DEFAULT_PORT = 8000

def run_server(port):
    Handler = http.server.SimpleHTTPRequestHandler
    
    # Allow port reuse to avoid "Address already in use" errors
    socketserver.TCPServer.allow_reuse_address = True
    
    try:
        with socketserver.TCPServer(("", port), Handler) as httpd:
            print(f"[*] Serving files from current directory at:")
            print(f"[*] http://localhost:{port}/")
            print("[*] Press Ctrl+C to stop.")
            httpd.serve_forever()
    except OSError as e:
        print(f"[!] Error: {e}")
    except KeyboardInterrupt:
        print("\n[*] Server stopped.")

if __name__ == "__main__":
    port = DEFAULT_PORT
    if len(sys.argv) > 1:
        try:
            port = int(sys.argv[1])
        except ValueError:
            print(f"[!] Invalid port '{sys.argv[1]}', using default {DEFAULT_PORT}")
            
    run_server(port)

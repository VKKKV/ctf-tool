#!/usr/bin/env python3
import socket
import sys

from scapy.all import Raw, send, sendp, sniff, sr, sr1, srp
from scapy.layers.inet import ICMP, IP, TCP, UDP
from scapy.layers.l2 import ARP, Ether, getmacbyip
from sympy.stats.matrix_distributions import rv

target_ip = "10.0.0.2"
payload = b"FLAG:10.0.0.1:31337"
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

try:
    s.bind(("0.0.0.0", 31337))
except OSError:
    print("Unable to bind to port 31337")
    sys.exit(1)

s.settimeout(3.0)

for port in range(1, 65535):
    s.sendto(payload, (target_ip, port))

try:
    data, addr = s.recvfrom(1024)
    print(f"\n[+] Flag: {data.decode().strip()}")
except socket.timeout:
    print("\n[-] Flag not found")

s.close()

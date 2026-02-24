#!/usr/bin/env python3
from scapy.all import rdpcap, sniff, sr1, srp
from scapy.layers.inet import ICMP, IP
from scapy.layers.l2 import ARP, Ether

packets = rdpcap("error_reporting.pcap")
flag = b""

for p in packets:
    # ICMP type 8 是 Echo Request（你发出的 ping 请求），而 type 0 是 Echo Reply（对方给你的 ping 回复）。
    # ICMP Exfiltration
    if p.haslayer(ICMP) and p[ICMP].type == 0 and p.haslayer("Raw"):
        flag += p["Raw"].load

with open("flag.jpg", "wb") as f:
    f.write(flag)

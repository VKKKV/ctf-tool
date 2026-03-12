#!/usr/bin/env python3
from scapy.all import send, sendp, sniff, sr1, srp, sr, Raw
from scapy.layers.inet import ICMP, IP, TCP, UDP
from scapy.layers.l2 import ARP, Ether, getmacbyip

ip_layer = IP(src="10.0.0.1", dst="10.0.0.2")

udp_layer = UDP(sport=31338, dport=31337)

raw_layer = Raw(b"Hello, World!\n")

ans =  sr1(ip_layer / udp_layer / raw_layer)

if ans and ans.haslayer(Raw):
    print(ans[Raw].load)


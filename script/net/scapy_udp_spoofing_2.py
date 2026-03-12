#!/usr/bin/env python3
import socket
import sys

from scapy.all import Raw, conf, send, sendp, sniff, sr, sr1, srp
from scapy.layers.inet import ICMP, IP, TCP, UDP
from scapy.layers.l2 import ARP, Ether, getmacbyip

source_ip = "10.0.0.3"
target_ip = "10.0.0.2"
payload = b"FLAG:10.0.0.1:4444"

ip_layer = IP(src=source_ip, dst=target_ip)
udp_layer = UDP(sport=31337, dport=(1, 65535))
raw_layer = Raw(payload)


def main():
    send(ip_layer / udp_layer / raw_layer, verbose=0)


if __name__ == "__main__":
    main()

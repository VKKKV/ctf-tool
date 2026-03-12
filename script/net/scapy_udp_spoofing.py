#!/usr/bin/env python3
import socket
import sys

from scapy.all import Raw, send, sendp, sniff, sr, sr1, srp
from scapy.layers.inet import ICMP, IP, TCP, UDP
from scapy.layers.l2 import ARP, Ether, getmacbyip
from sympy.stats.matrix_distributions import rv

# nc -u -l -p 31337
target_ip = "10.0.0.2"
payload = b"FLAG:10.0.0.1:31338"

ip_layer = IP(src="10.0.0.1", dst=target_ip)
raw_layer = Raw(payload)


def main(dport):
    udp_layer = UDP(sport=31337, dport=dport)

    send(ip_layer / udp_layer / raw_layer, verbose=0)
    # ans = sr1(ip_layer / udp_layer / raw_layer, timeout=2, verbose=0)
    #
    # if ans and ans.haslayer(Raw):
    #     print(ans[Raw].load)
    #     exit()


if __name__ == "__main__":
    # main()
    for i in range(1, 65535):
        if i % 1000 == 0:
            print(f"[*] Trying {i}")
        main(dport=i)

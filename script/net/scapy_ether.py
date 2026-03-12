#!/usr/bin/env python3
from scapy.all import sendp, sniff, sr1, srp
from scapy.layers.inet import ICMP, IP
from scapy.layers.l2 import ARP, Ether, getmacbyip

source_mac = "aa:98:41:69:f7:79"
target_mac = "ff:ff:ff:ff:ff:ff"

packet = Ether(src=source_mac, dst=target_mac, type=0xFFFF)
sendp(packet, iface="eth0")

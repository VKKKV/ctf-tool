#!/usr/bin/env python3
from scapy.all import sendp, sniff, sr1, srp, send
from scapy.layers.inet import ICMP, IP
from scapy.layers.l2 import ARP, Ether, getmacbyip

source_ip = "0.0.0.0"
target_ip = "10.0.0.2"

packet = IP(src=source_ip, dst=target_ip, proto=0xff)
send(packet, iface="eth0")

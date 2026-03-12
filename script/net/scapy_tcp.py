#!/usr/bin/env python3
from scapy.all import send, sendp, sniff, sr1, srp
from scapy.layers.inet import ICMP, IP, TCP, UDP
from scapy.layers.l2 import ARP, Ether, getmacbyip

# Manually send a Transmission Control Protocol packet. The packet should have TCP sport=31337, dport=31337, seq=31337, ack=31337, flags=APRSF. The packet should be sent to the remote host at 10.0.0.2.

source_ip = "0.0.0.0"
target_ip = "10.0.0.2"

# packet = IP(src=source_ip, dst=target_ip) / TCP(
#     sport=31337, dport=31337, seq=31337, ack=31337, flags="APRSF"
# )

# Manually perform a Transmission Control Protocol handshake. The initial packet should have TCP sport=31337, dport=31337, seq=31337. The handshake should occur with the remote host at 10.0.0.2.

packet = IP(src=source_ip, dst=target_ip) / TCP(sport=31337, dport=31337, seq=31337)

send(packet, iface="eth0")

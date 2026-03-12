#!/usr/bin/env python3
from scapy.all import send, sendp, sniff, sr1, srp
from scapy.layers.inet import ICMP, IP, TCP, UDP
from scapy.layers.l2 import ARP, Ether, getmacbyip

# 1. 构造底层 IP 头
ip_layer = IP(dst="10.0.0.2")

syn_layer = TCP(sport=31337, dport=31337, seq=31337, flags="S")

print("[*] Sending SYN...")
# 使用 sr1 (send and receive 1) 发送包并等待回复
syn_ack_packet = sr1(ip_layer / syn_layer, timeout=2)

if syn_ack_packet and syn_ack_packet.haslayer(TCP):
    print(
        f"[*] Received SYN-ACK! Server SEQ: {syn_ack_packet[TCP].seq}, Server ACK: {syn_ack_packet[TCP].ack}"
    )

    # 3. 构造并发送 ACK 包 (Step 3)
    # 我们的 seq 应该是对方期望的 ack (也就是我们初始 seq + 1 = 31338)
    # 我们的 ack 应该是对方的 seq + 1
    ack_layer = TCP(
        sport=31337,
        dport=31337,
        flags="A",
        seq=syn_ack_packet[TCP].ack,
        ack=syn_ack_packet[TCP].seq + 1,
    )

    print("[*] Sending ACK...")
    send(ip_layer / ack_layer)

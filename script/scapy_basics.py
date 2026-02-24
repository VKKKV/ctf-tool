#!/usr/bin/env python3
from scapy.all import rdpcap, sniff, sr1, srp, Raw
from scapy.layers.inet import ICMP, IP, UDP, TCP
from scapy.layers.l2 import ARP, Ether


def myread():
    packets = rdpcap("./error_reporting.pcap")
    for packet in packets:
        if packet.haslayer(TCP) and packet.haslayer(Raw):
            payload = packet[Raw].load
            if b"flag{" in payload:
                print(payload)


def packet_callback(pkt):
    print(pkt.summary())


if __name__ == "__main__":
    packet = IP(dst="192.168.1.1") / TCP(dport=80, flags="S") / b"I use Arch btw"
    response = sr1(packet, timeout=2)
    sniff(iface="enp7s0", filter="icmp", prn=packet_callback, count=10)

#!/usr/bin/env python3
from scapy.all import Raw, conf, send, sendp, sniff, sr, sr1, srp
from scapy.layers.inet import ICMP, IP, TCP, UDP
from scapy.layers.l2 import ARP, Ether, getmacbyip

def extract_flag(pkt):
    if pkt.haslayer(Raw):
        payload = pkt[Raw].load.decode('utf-8', errors='ignore').strip()
        client_ip = pkt[IP].src
        client_port = pkt[UDP].sport
        print(f"[+] 抓到来自 {client_ip}:{client_port} 的数据! Payload: {payload}")

def main():
    print("[*] 遵循 The Arch Way: BPF Filter 已注入，正在嗅探 UDP 4444 端口...")
    # BPF (Berkeley Packet Filter)
    sniff(filter="udp and dst port 4444", prn=extract_flag, store=0)

if __name__ == "__main__":
    main()

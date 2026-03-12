#!/usr/bin/env python3
import logging
import socket
import sys

from scapy.all import Raw, send, sendp, sniff, sr, sr1, srp
from scapy.layers.inet import ICMP, IP, TCP, UDP
from scapy.layers.l2 import ARP, Ether, getmacbyip
from sympy.stats.matrix_distributions import rv

# not work
logging.getLogger("scapy.runtime").setLevel(logging.ERROR)

target_ip = "10.0.0.2"
payload = b"FLAG:10.0.0.1:31337"

print("start")

# 魔法就在这里：dport=(32768, 61000) 会让 Scapy 自动把这个包展开成 28000+ 个包！
# sport 必须是 31337 才能骗过验证
magic_packet = IP(dst=target_ip) / UDP(sport=31337, dport=(1, 65535)) / Raw(payload)

# sr() 会把这几万个包全发出去，并且同时利用 BPF 在底层抓取匹配的回包。
# timeout=3 确保发完最后一个包后，再等 3 秒钟 Flag 飞回来。
# multi=True 允许一个请求对应多个响应（虽然我们只需要一个）
ans, unans = sr(magic_packet, timeout=3, verbose=0, multi=True)

# 遍历收到的所有回包
for snd, rcv in ans:
    if rcv.haslayer(Raw):
        print(f"\n[+] {rcv[UDP].sport} 的 Flag:")
        print(rcv[Raw].load.decode().strip())
        exit(0)

print("failed")

#!/usr/bin/env python3
import glob
import os

from cryptography import x509
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives.asymmetric.rsa import RSAPrivateKey, RSAPublicKey
from scapy import dadict
from scapy.all import *
from scapy.all import PcapReader, Raw, load_layer, rdpcap, sniff, sr1, srp
from scapy.layers.inet import ICMP, IP, TCP
from scapy.layers.l2 import ARP, Ether
from scapy.layers.tls.all import TLS
from scapy.layers.tls.cert import Cert
from scapy.layers.tls.handshake import TLSCertificate
from scapy.sessions import TCPSession

PCAP_FILE = (
    "/home/kita/Downloads/24ec9b75de3c273d2765622deb3c7f742b87cf6b/merged_chall.pcap"
)
OUTPUT = "output.bin"

BPF_FILTER = "tcp"

packets = sniff(offline=PCAP_FILE, filter=BPF_FILTER, session=TCPSession)

print(f"[*] 正在使用 Scapy 解析 {PCAP_FILE}")

data = b""

for pkt in packets:
    if TCP in pkt and Raw in pkt:
        payload = bytes(pkt[Raw].load)
        data += payload

with open(OUTPUT, "wb") as f:
    f.write(data)

print(f"[+] 提取的数据已写入 {OUTPUT}")

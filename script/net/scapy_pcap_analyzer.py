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
from scapy.all import Raw, load_layer, rdpcap
from scapy.layers.inet import IP, TCP
from scapy.layers.smb import *
from scapy.layers.tls.all import TLS
from scapy.layers.tls.cert import Cert
from scapy.layers.tls.handshake import TLSCertificate

PCAP_FILE = "/home/kita/Downloads/commutative_payload.pcap"
KEYS = "/home/kita/Downloads/keys/"

load_layer("tls")

def show_pcap(pcap_path):
    packets = rdpcap(pcap_path)
    packets.show()

def check_pcap(pcap_path):
    packets = rdpcap(pcap_path)
    for pkt in packets:
        pkt.show()
        if pkt.haslayer(Raw):
            raw = pkt[Raw].load
            try:
                if b"flag" in raw.lower() or b"ctf" in raw.lower():
                    print(f"[+] Found flag: {raw}")
                    exit()
                print(raw.decode())
            except Exception as e:
                print(f"[-] Error: {e}")
                continue

def check_smb(pcap_path):
    packets = rdpcap(pcap_path)
    pass


def print_raw(pcap_path):
    packets = rdpcap(pcap_path)
    for pkt in packets:
        if TCP in pkt and pkt.haslayer(Raw):
            raw = pkt[Raw].load
            try:
                print(raw.decode(errors="ignore"))
            except Exception as e:
                print(f"[-] Error: {e}")
                continue


def print_hex(pcap_path):
    packets = rdpcap(pcap_path)
    for pkt in packets:
        if TCP in pkt and pkt.haslayer(Raw):
            raw = pkt[Raw].load
            h = raw.decode(errors="ignore")
            try:
                print(raw)
                print(decode_hex_str(h))
                print("-"*30)
            except Exception as e:
                print(f"[-] Error: {e}")
                continue

def print_hex_search(pcap_path, s):
    packets = rdpcap(pcap_path)
    for pkt in packets:
        if TCP in pkt and pkt.haslayer(Raw):
            raw = pkt[Raw].load
            h = raw.decode()
            try:
                if s in raw:
                    print(raw)
                    print(h)
                    print("\n")
                    print(raw.hex())
                    print(decode_hex_str(h))
                    print("-"*30)
            except Exception as e:
                print(f"[-] Error: {e}")
                continue

def decode_hex_str(hex_str):
    return bytes.fromhex(hex_str)


if __name__ == "__main__":
    # show_pcap(PCAP_FILE)
    check_pcap(PCAP_FILE)
    # print_hex(PCAP_FILE)
    # print_hex_search(PCAP_FILE, b"b925afc100")

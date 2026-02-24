#!/usr/bin/env python3
"""
Scapy Learning Example
A cleaned and structured script demonstrating ICMP pinging, ARP scanning, and packet sniffing.
Note: Raw socket operations (sending/sniffing) usually require root privileges.
"""

import logging

from scapy.all import sniff, sr1, srp
from scapy.layers.inet import ICMP, IP
from scapy.layers.l2 import ARP, Ether

# Set Scapy's log level to error to reduce noise
logging.getLogger("scapy.runtime").setLevel(logging.ERROR)


def ping_host(target: str, timeout: int = 2) -> None:
    """
    Sends an ICMP Echo Request (ping) to a target IP and prints the response.
    """
    print(f"\n--- Pinging {target} ---")

    # Create an IP packet with an ICMP layer
    # IP(dst=...) sets the destination IP
    # ICMP() defaults to an Echo Request
    packet = IP(dst=target) / ICMP()

    # sr1: Send at Layer 3 and receive only the first response
    response = sr1(packet, timeout=timeout, verbose=False)

    if response and response.haslayer(IP):
        print(f"[+] Received response from {response[IP].src}")
    else:
        print(f"[-] No response from {target} (Timed out)")


def arp_scan(subnet: str, timeout: int = 2) -> None:
    """
    Performs an ARP scan on the specified subnet to discover active hosts.
    """
    print(f"\n--- ARP Scan: {subnet} ---")

    # Ether(dst="ff:ff:ff:ff:ff:ff") creates a Broadcast Ethernet frame
    # ARP(pdst=subnet) creates an ARP request for the given range
    ether_layer = Ether(dst="ff:ff:ff:ff:ff:ff")
    arp_layer = ARP(pdst=subnet)
    packet = ether_layer / arp_layer

    # srp: Send and Receive packets at Layer 2
    # Returns two lists: answered and unanswered
    answered, _ = srp(packet, timeout=timeout, verbose=False)

    if answered:
        print(f"{'IP Address':<15} | {'MAC Address':<17}")
        print("-" * 35)
        for sent, received in answered:
            # received[ARP].psrc is the Source Protocol (IP) address
            # received[Ether].src is the Source Hardware (MAC) address
            print(f"{received[ARP].psrc:<15} | {received[Ether].src:<17}")
    else:
        print("[-] No hosts found in the specified subnet.")


def capture_packets(count: int = 5) -> None:
    """
    Sniffs a specified number of packets and displays a summary.
    """
    print(f"\n--- Sniffing {count} Packets ---")

    # sniff: Capture packets from the network interface
    # count: number of packets to capture
    packets = sniff(count=count)

    # summary() provides a quick high-level overview of the captured packets
    packets.summary()


def main():
    # Target for ICMP Ping (Google Public DNS)
    # ping_host("8.8.8.8")

    # Local Subnet for ARP Scan (Adjust to your local network range)
    # Common ranges: 192.168.0.0/24, 10.0.0.0/24
    # arp_scan("192.168.0.0/24")

    # Capture traffic
    capture_packets(5)
    pass


if __name__ == "__main__":
    main()

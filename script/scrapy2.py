#!/usr/bin/env python3
import glob
import os

from cryptography import x509
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.rsa import RSAPrivateKey, RSAPublicKey
from scapy.all import Raw, load_layer, rdpcap
from scapy.layers.inet import IP, TCP
from scapy.layers.tls.cert import Cert
from scapy.layers.tls.handshake import TLSCertificate
from scapy.layers.tls.record import TLS

load_layer("tls")

PCAP_FILE = "/home/kita/Downloads/encrypted.pcap"
KEYS = "/home/kita/Downloads/keys/"

packets = rdpcap(PCAP_FILE)


def get_target_modulus(pcap_path):
    print(f"[*] Reading {pcap_path} ...")
    packets = rdpcap(pcap_path)

    for pkt in packets:
        print("TLS in packet:", TLS in pkt)
        # Check if the packet contains a TLS layer and a Certificate handshake message
        if TLS in pkt and pkt[TLS].msg and isinstance(pkt[TLS].msg[0], TLSCertificate):
            # The certificates are in a list within the TLSCertificate object
            cert_list = pkt[TLS].msg[0].certs
            print(f"[+] Found {len(cert_list)} certificates in a packet:")

            for cert in cert_list:
                # 'cert' is an X509Cert object, which can be shown or summarized
                print(cert.summary())
                # print(cert.show()) # For detailed information
                # You can also access specific fields like the subject or issuer
                # print(f"Subject: {cert.subject.native}")
                # print(f"Issuer: {cert.issuer.native}")

            # Extract the public key from the first certificate
            try:
                cert_bytes = cert_list[0].data
                cert = x509.load_der_x509_certificate(cert_bytes, default_backend())
                public_key = cert.public_key()

                # 提取 Modulus (N)
                if not isinstance(public_key, RSAPublicKey):
                    print("[-] Not an RSA public key.")
                    return None

                return public_key.public_numbers().n

            except Exception as e:
                print(f"[-] Error parsing certificate: {e}")
                return None

    print("[-] No TLS Certificate found in the PCAP.")
    return None


def find_matching_private_key(target_modulus, keys_directory):
    print(f"[*] Searching for matching private key in {keys_directory} ...")

    # 遍历目录下的所有 PEM 私钥文件
    for key_file in glob.glob(os.path.join(keys_directory, "*.pem")):
        try:
            with open(key_file, "rb") as f:
                private_key = serialization.load_pem_private_key(
                    f.read(), password=None, backend=default_backend()
                )

            if not isinstance(private_key, RSAPrivateKey):
                print("[-] Not an RSA private key.")
                continue

            # 提取私钥的 Modulus
            priv_modulus = private_key.private_numbers().public_numbers.n

            if priv_modulus == target_modulus:
                print(f"[!] BINGO! Matching key found: {key_file}")
                return key_file
        except Exception:
            continue

    print("[-] No matching key found.")
    return None


if __name__ == "__main__":
    target_mod = get_target_modulus(PCAP_FILE)

    if target_mod:
        print(f"[+] Target Modulus (Hex): {hex(target_mod)[:50]}...")
        find_matching_private_key(target_mod, KEYS)

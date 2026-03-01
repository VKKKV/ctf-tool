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
from scapy.layers.tls.all import TLS
from scapy.layers.tls.cert import Cert
from scapy.layers.tls.handshake import TLSCertificate

PCAP_FILE = "/home/kita/Downloads/00ps.pcap"
KEYS = "/home/kita/Downloads/keys/"

load_layer("tls")


def find_cert(pcap_path):
    packets = rdpcap(pcap_path)
    cert_list = []

    for pkt in packets:
        if pkt.haslayer(Raw):
            raw = pkt[Raw].load
            try:
                tls_parsed = TLS(raw)
                tls_cert_layer = tls_parsed.getlayer(TLSCertificate)
                if tls_cert_layer:
                    print("[-] Found TLS Certificate.")
                    cert = tls_cert_layer.certs
                    for _, x509_wrapper in cert:
                        cert_list.append(x509_wrapper)
                        print("[-] Extracted a TLS Certificate.")
                else:
                    print("[-] Found TLS packet.")
            except Exception as e:
                print(f"[-] Error: {e}")
                continue
    return cert_list


def read_key(key_file):
    with open(key_file, "rb") as f:
        private_key = serialization.load_pem_private_key(
            f.read(), password=None, backend=default_backend()
        )
    return private_key


def find_matching_private_key(target_modulus: int, keys_directory: str) -> str | None:
    print(f"[*] Searching for matching private key in {keys_directory} ...")

    for key_file in glob(os.path.join(keys_directory, "*")):
        try:
            private_key = read_key(key_file)
            # 类型守卫
            if isinstance(private_key, rsa.RSAPrivateKey):
                priv_modulus = private_key.private_numbers().public_numbers.n
                if priv_modulus == target_modulus:
                    print(f"[!] BINGO! Matching key found: {key_file}")
                    return key_file
        except Exception:
            pass  # 静默忽略无法解析的非私钥文件

    print("[-] No matching key found.")
    return None


def get_modulus(cert_obj):
    assert isinstance(cert_obj, Cert)
    pubkey_bytes = cert_obj.pubKey.der

    try:
        public_key = serialization.load_der_public_key(pubkey_bytes)

        if not isinstance(public_key, rsa.RSAPublicKey):
            print("[-] Not an RSA public key.")
            return None

        # 3. 提取 Modulus (N)
        return public_key.public_numbers().n

    except ValueError as e:
        print(f"[-] Failed to parse public key: {e}")
        return None


def get_key_modulus(private_key):
    if isinstance(private_key, rsa.RSAPrivateKey):
        priv_modulus = private_key.private_numbers().public_numbers.n
        return priv_modulus
    else:
        return None


def get_exponent(cert_obj):
    assert isinstance(cert_obj, Cert)
    pubkey_bytes = cert_obj.pubKey.der

    try:
        public_key = serialization.load_der_public_key(pubkey_bytes)

        if not isinstance(public_key, rsa.RSAPublicKey):
            print("[-] Not an RSA public key.")
            return None

        # 3. 提取 Exponent (e)
        return public_key.public_numbers().e

    except ValueError as e:
        print(f"[-] Failed to parse public key: {e}")
        return None


if __name__ == "__main__":
    pass
    # private_key = read_key("/home/kita/Downloads/private_key.pem")
    # print(private_key)
    # n = get_key_modulus(private_key)
    # print(n)

    # cert_list = find_cert(PCAP_FILE)
    # print(cert_list)
    # for cert_obj in cert_list:
    #     modulus = get_modulus(cert_obj)
    #     exponent = get_exponent(cert_obj)
    #     print(modulus)
    #     print(exponent)

    # if modulus:
    #     key_path = find_matching_private_key(modulus, KEYS)
    #     print(key_path)

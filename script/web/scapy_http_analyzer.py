#!/usr/bin/env python3
"""
Scapy HTTP/Webshell Traffic Analyzer
------------------------------------
A specialized utility for extracting and decrypting payloads from PCAP files,
targeting traffic typical of PHP webshells (e.g., Behinder, AntSword).
Includes logic for XOR decryption, Zlib decompression, and flag assembly.
"""

import base64
import re
import urllib.parse
import zlib

from scapy.all import *

# --- Configuration & Constants ---
PCAP_FILE = "/home/kita/Downloads/web_shell.pcap"

# Cryptographic Keys (Typical for Behinder/Godzilla style webshells)
KEY = b"81aebe18"
KH = b"775d4f83f4e0"  # Header marker
KF = b"0120dd0bccc6"  # Footer marker
KP = b"kkqES1eCIzoxyHXb"  # Response prefix

# Global state for flag extraction
flag_data = {}  # Maps offset -> character
current_offset = -1

# --- Logic Functions ---


def decrypt_payload(b64_data):
    """
    Decrypts a payload using the sequence: URL Decode -> Base64 -> XOR -> Zlib.
    """
    try:
        # 1. URL Decode
        clean_data = urllib.parse.unquote_to_bytes(b64_data)

        # 2. Fix Base64 padding if necessary
        clean_data += b"=" * (-len(clean_data) % 4)
        decoded = base64.b64decode(clean_data)

        # 3. XOR Decryption
        k_len = len(KEY)
        xored = bytearray(a ^ KEY[i % k_len] for i, a in enumerate(decoded))

        # 4. Zlib Decompression
        return zlib.decompress(xored).decode("utf-8", errors="ignore")
    except Exception as e:
        return f"[!] Decryption Error: {e}"


def extract_flag_fragment(raw_text):
    """
    Parses decrypted output to identify flag fragments extracted via 'xxd'.
    Expects 'xxd -p -l1 -s[offset]' in request and 2-char hex in response.
    """
    global current_offset
    raw_text = raw_text.strip()
    if not raw_text:
        return

    # Match Request: Extract offset from xxd command
    if "xxd -p -l1 -s" in raw_text:
        match = re.search(r"-s(\d+)", raw_text)
        if match:
            current_offset = int(match.group(1))

    # Match Response: If we have an offset, convert hex response to char
    elif current_offset != -1 and re.match(r"^[0-9a-fA-F]{2}$", raw_text):
        try:
            char = bytes.fromhex(raw_text).decode("utf-8")
            flag_data[current_offset] = char
            print(
                f"[\033[92m+\033[0m] Fragment Found: Offset {current_offset:02} -> '{char}'"
            )
        except Exception as e:
            print(f"[-] Decode error: {e}")
        finally:
            current_offset = -1


def process_pcap(packets, regex):
    """Iterates through packets, searching for encrypted payloads via regex."""
    print(f"[*] Analyzing {len(packets)} packets...")

    for i, p in enumerate(packets):
        if p.haslayer(Raw):
            raw_payload = p[Raw].load
            match = re.search(regex, raw_payload)
            if match:
                decrypted = decrypt_payload(match.group(1))
                print(f"[*] Packet {i + 1} matched.")
                # print(f"Raw: {match.group(1)[:50]}...") # Debug
                print(f"Decrypted: {decrypted}")

                extract_flag_fragment(decrypted)
                print("-" * 30)


def print_final_flag():
    """Sorts fragments by offset and prints the assembled flag."""
    if not flag_data:
        print("\n[-] No flag fragments found in the analyzed packets.")
        return

    sorted_chars = [flag_data[k] for k in sorted(flag_data.keys())]
    final_flag = "".join(sorted_chars)

    print("\n" + "=" * 40)
    print("\033[93m[*] FINAL ASSEMBLED FLAG:\033[0m")
    print(f"\033[96m{final_flag}\033[0m")
    print("=" * 40 + "\n")


# --- Debug Utilities ---


def check_packet_by_content(packets, content):
    """Heuristic search for specific raw bytes in a PCAP."""
    for i, p in enumerate(packets):
        if p.haslayer(Raw) and content in p[Raw].load:
            print(f"[*] Content found in Packet {i + 1}")
            print(p[Raw].load.decode(errors="ignore"))


# --- Main Execution ---

if __name__ == "__main__":
    try:
        # Load necessary layers
        load_layer("tls")

        # Load PCAP
        pkts = rdpcap(PCAP_FILE)

        # Regex to capture content between specific webshell markers
        payload_regex = KH + b"(.+?)" + KF

        # Execute analysis
        process_pcap(pkts, payload_regex)
        print_final_flag()

    except FileNotFoundError:
        print(f"[-] Error: PCAP file not found at {PCAP_FILE}")
    except Exception as e:
        print(f"[-] Fatal error: {e}")

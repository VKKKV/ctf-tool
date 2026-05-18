#!/usr/bin/env python3
import socket
import struct
from dnslib import DNSRecord, DNSQuestion, QTYPE, TXT, RR

def send_query(sock, dns_bytes):
    """Send a length-prefixed DNS query and return the raw response."""
    length = len(dns_bytes)
    sock.sendall(struct.pack(">H", length) + dns_bytes)
    resp_len = struct.unpack(">H", sock.recv(2))[0]
    return sock.recv(resp_len)

# 1. Connect
HOST = "challs.umdctf.io"
PORT = 32323
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect((HOST, PORT))

# 2. Build the bulk query – 819 TXT questions, each for index 0..818
q = DNSRecord()
for i in range(819):
    # Append a DNSQuestion object directly to the questions list
    q.questions.append(DNSQuestion(f"{i}.inside.info", QTYPE.TXT))
query_bytes = q.pack()

raw_resp = send_query(sock, query_bytes)
response = DNSRecord.parse(raw_resp)

# 3. Extract secret characters (answers come in the same order)
secret_chars = []
for rr in response.rr:
    # TXT rdata contains a list of byte strings; ours has exactly one
    secret_chars.append(rr.rdata.data[0].decode())
secret = "".join(secret_chars)
assert len(secret) == 819, f"Expected 819 chars, got {len(secret)}"
print("[*] Secret recovered")

# 4. Reconstruct the subdomain: 63-char chunks joined by '.'
chunks = [secret[i:i+63] for i in range(0, 819, 63)]
subdomain = ".".join(chunks)
flag_qname = f"{subdomain}.inside.info"

# 5. Ask for the flag
flag_query = DNSRecord()
flag_query.questions.append(DNSQuestion(flag_qname, QTYPE.TXT))

raw_resp2 = send_query(sock, flag_query.pack())
response2 = DNSRecord.parse(raw_resp2)

# 6. Print the flag
for rr in response2.rr:
    if rr.rname == "flag.inside.info.":   # note the trailing dot
        flag = b"".join(rr.rdata.data).decode()
        print(f"[+] Flag: {flag}")

sock.close()

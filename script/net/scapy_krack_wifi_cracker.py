import binascii

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from scapy.all import rdpcap
from scapy.layers.dot11 import Dot11, Dot11CCMP, Dot11QoS

PCAP_FILE = "/home/kita/Downloads/00ps.pcap"


def crack_temporal_zeros(pcap_file):
    print(f"[*] Parsing {pcap_file}...")
    try:
        packets = rdpcap(pcap_file)
    except Exception as e:
        print(f"[!] File error. Error: {e}")
        return

    # CVE-2017-13077 (KRACK): The bug forces the TK (Temporal Key) to all zeros.
    tk_all_zeros = b"\x00" * 16

    for idx, pkt in enumerate(packets):
        if not pkt.haslayer(Dot11CCMP):
            continue

        ccmp = pkt[Dot11CCMP]

        # 1. 提取 Packet Number (PN), 6 bytes, 从高位到低位组合
        pn = bytes([ccmp.PN5, ccmp.PN4, ccmp.PN3, ccmp.PN2, ccmp.PN1, ccmp.PN0])

        # 2. 提取 Transmitter Address (A2), 6 bytes
        try:
            mac_a2 = binascii.unhexlify(pkt[Dot11].addr2.replace(":", ""))
        except AttributeError:
            continue  # Malformed frame, drop it. We don't do bloat error handling.

        # 3. 提取 QoS Priority (TID), 1 byte. 如果没有 QoS layer 默认为 0
        priority = b"\x00"
        if pkt.haslayer(Dot11QoS):
            # QoS 控制字段的低 4 位是 TID
            tid = pkt[Dot11QoS].TID & 0x0F
            priority = bytes([tid])

        # 4. 构造 13 字节的 CCM Nonce
        # Nonce = Priority (1 byte) + MAC A2 (6 bytes) + PN (6 bytes)
        nonce = priority + mac_a2 + pn

        # 5. 组装 CTR 模式的 Initial Vector (16 bytes)
        # 格式: [Flags(1 byte)] + [Nonce(13 bytes)] + [Counter(2 bytes)]
        # 在 802.11 CCMP 中，Flags 固定为 0x01 (表示 L=2)。加密数据块的 Counter 从 1 开始。
        iv = b"\x01" + nonce + b"\x00\x01"

        # 6. 用 AES-CTR 模式暴力解密，完美绕过 AAD/MIC 校验
        cipher = Cipher(
            algorithms.AES(tk_all_zeros), modes.CTR(iv), backend=default_backend()
        )
        decryptor = cipher.decryptor()

        # CCMP 负载的最后 8 字节是 MIC，前面才是密文
        raw_data = ccmp.data
        if len(raw_data) <= 8:
            continue

        ciphertext = raw_data[:-8]
        plaintext = decryptor.update(ciphertext) + decryptor.finalize()

        # CTF 的 flag 通常是可打印字符，我们只看 ASCII 部分
        try:
            # 去除 LLC/SNAP 头部 (通常是前 8 字节)，直接找明文
            decoded_text = plaintext.decode("utf-8", errors="ignore")
            if "247ctf" in decoded_text.lower():
                print(f"\n[+] Flag found in packet #{idx + 1}:")
                print(f"    Hex Dump: {binascii.hexlify(plaintext[:30])}...")
                print(f"    Plaintext: {decoded_text}\n")
                break
        except Exception:
            pass


if __name__ == "__main__":
    crack_temporal_zeros(PCAP_FILE)

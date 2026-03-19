# CTF Toolkit

A collection of tools, scripts, and resources for CTF competitions and security research.

## Core Technologies

- **Languages:** Python 3, PHP, Shell, C
- **Key Libraries:** pwntools, scapy, requests, angr, PyCryptodome
- **Integrated Tools:** SecLists, PayloadsAllTheThings, Ghidra, IDA, dnSpy, GTFOBins, HackTricks

## Directory Structure

### `script/` — Custom Scripts

| Category | Scripts | Description |
|----------|---------|-------------|
| `crypto/` | 40 | AES-ECB/CBC exploits (CPA, padding oracle, bit-flip), RSA attacks, DHKE, XOR/OTP, SHA PoW, TLS forgery |
| `net/` | 20 | Scapy packet crafting (ARP, TCP, UDP, ICMP), PCAP analysis, MITM, KRACK WiFi, spoofing |
| `pwn/` | 17 | Buffer overflow, shellcode injection, NOP sleds, PIE bypass, ROP, angr-assisted exploits |
| `reverse/` | 21 | cIMG format exploitation suite (14 variants), angr symbolic execution, radare2 debugging, bcrypt cracking |
| `web/` | 13 | HTTP request templates, blind SQLi tools, Flask session decoding, Heartbleed PoC |
| `forensics/` | 3 | PNG dimension brute-force, image byte fixer, coordinate plotter |
| `shell/` | 5 | PHP web shells, reverse shells, linpeas, pspy64, rootshell.c |
| `utils/` | 5 | Base64, data format converter, payload generator, TCP client, DB log analyzer |

### Top-Level Directories

| Directory | Description |
|-----------|-------------|
| `dict/` | Wordlists — SecLists, rockyou, wister, custom dictionaries |
| `web/` | Exploitation frameworks — Behinder, AntSword, PayloadsAllTheThings, PEASS-ng, PowerSploit, nishang, SSRFmap, GitTools, GTFOBins, HackTricks, xsser |
| `reverse/` | RE tools — IDA themes (long_night), Ghidra themes, dnSpyEx, ida-pro-mcp, ret-sync |
| `forensis/` | OS symbol tables for Volatility |
| `misc/` | Steganography tools (bftools, qrazybox), file magic numbers, archive utilities |

## Usage

Most scripts are standalone Python 3:

```bash
python3 script/<category>/<script_name>.py
```

Reference docs are available in `script/`:
- `pwntools_cheatsheet.md` — pwntools quick reference
- `note.md` — x86 assembly and syscall references
- `ansi.md` — ANSI escape code reference

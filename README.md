# CTF Toolkit & Workspace

A comprehensive collection of tools, scripts, and resources for Capture The Flag (CTF) competitions and security research.

## 🚀 Overview

This workspace is organized into functional modules covering various areas of cybersecurity, serving as both an automation repository and a local knowledge base.

### 🛠 Core Technologies
- **Languages:** Python 3, PHP, Shell, C.
- **Key Libraries:** `pwntools`, `requests`, `base64`, `hashlib`.
- **Integrated Tools:** SecLists, PayloadsAllTheThings, Ghidra, IDA, dnSpy.

## 📁 Directory Structure

- **`script/`**: Custom scripts for Crypto, Forensics, Pwn, and Web.
- **`dict/`**: Massive collection of wordlists (SecLists, rockyou, etc.).
- **`web/`**: Exploitation frameworks (Behinder, AntSword) and vulnerability scanners.
- **`reverse/`**: Reverse engineering tools and configurations.
- **`forensis/`**: OS symbol tables and forensic utilities.
- **`misc/`**: Steganography and archive recovery tools.

## 📖 Usage

### Running Scripts
Most utilities are standalone Python 3 scripts:
```bash
python3 script/<category>/<script_name>.py
```

### Development
- **Utils**: Use `script/utils/` for common data transformations.
- **Solves**: Add challenge-specific solvers to `script/solves/`.
- **Templates**: See `script/request.py` or `script/pwn/pwntools_example.py` for starting points.

---
*Maintained for CTF excellence.*

# CTF Toolkit & Workspace

This directory is a comprehensive collection of tools, scripts, and resources for Capture The Flag (CTF) competitions and security research. It includes both well-known third-party tools and custom utilities tailored for various challenge categories.

## Project Overview

The workspace is organized into functional modules covering different areas of cybersecurity. It serves as both a repository of automated scripts and a local knowledge base for exploitation techniques.

### Core Technologies
- **Languages:** Primarily Python 3, with some PHP and Shell scripts.
- **Frameworks/Libraries:** `requests`, `pwntools`, `base64`, `hashlib`, etc.
- **Tools:** Integration with SecLists, PayloadsAllTheThings, Ghidra, IDA, and more.

## Directory Structure

### 📂 `script/`
Custom Python and PHP scripts for various CTF categories.
- **`crypto/`**: Cryptographic attacks and mathematical utilities (e.g., GCD, XOR, Prime math).
- **`forensics/`**: Scripts for image fixing and file header manipulation (e.g., `png_utils.py`).
- **`pwn/`**: Exploitation templates using `pwntools` and stack extractor scripts.
- **`solves/`**: Specific challenge solvers (e.g., ECB forgery, TCP automation).
- **`utils/`**: General-purpose utilities for data format conversion (Hex/Base64) and network interaction.
- **`web/`**: Web-specific scripts like Blind SQLi automation and Flask session managers.

### 📂 `dict/`
A massive collection of wordlists and dictionaries for brute-forcing.
- **`SecLists/`**: A local clone of the industry-standard security lists.
- **`rockyou.txt`**: The classic password wordlist.
- **`MyDict/` & `逸尘的字典`**: Categorized wordlists for usernames, passwords, paths, and vulnerabilities.

### 📂 `web/`
Reference materials and automated exploitation tools.
- **`hacktricks/` & `PayloadsAllTheThings/`**: Comprehensive local clones of web exploitation guides.
- **`Behinder` & `AntSword`**: Webshell management frameworks.
- **`SSRFmap`, `GitTools`, `xsser`**: Specialized web vulnerability scanners.

### 📂 `reverse/` & `forensis/`
- **`reverse/`**: IDA scripts, Ghidra themes, and .NET decompiler (dnSpy) configurations.
- **`forensis/`**: Symbol tables for various operating systems (Linux, Mac, Windows) and specialized forensic tools.

### 📂 `misc/`
- **`steg/`**: Steganography tools (Stegsolve, BlindWaterMark, Jphswin).
- **Compression**: Tools for archive password recovery (archpr, yafu).

## Usage & Development

### Running Scripts
Most scripts in the `script/` directory are standalone Python files.
- **Requirements:** Ensure Python 3 is installed. Some scripts may require `requests` or `pwntools`.
- **Execution:** `python3 script/category/script_name.py`

### Development Conventions
- **Hardcoded Data:** Many scripts in `solves/` contain hardcoded URLs or data from specific challenges. Always review and update these values before running.
- **Modular Utilities:** Prefer using the scripts in `script/utils/` for common tasks like Base64 encoding/decoding or Hex conversion.
- **Testing:** When adding a new solver, consider adding it to `script/solves/` with a descriptive name.

## Key Files
- `script/request.py`: A basic template for HTTP-based challenge interaction.
- `script/utils/data_format_converter.py`: A handy tool for converting decimal ASCII arrays to various formats.
- `web/exploit-notes/`: A local repository for general exploitation notes.

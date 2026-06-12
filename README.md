# CTF Toolkit

Personal CTF and security-research workspace. It is a toolbox repo, not a single packaged application.

The repo has two different kinds of content:

- `script/` is the local working area: helper scripts, exploit templates, notes, and disposable challenge utilities.
- most other top-level directories are vendored references, third-party tools, or git submodules.

## Quick Start

Clone with submodules if you want the full reference set:

```bash
git clone --recurse-submodules <repo-url>
cd tool
```

If the repo is already cloned:

```bash
git submodule update --init --recursive
```

Set up the Python environment for `script/` using **uv** (requires Python >=3.12):

```bash
cd script
uv venv
source .venv/bin/activate
uv sync
```

Run custom scripts directly:

```bash
uv run script/<category>/<name>.py
```

Examples:

```bash
uv run script/crypto/xor_cipher_tool.py
uv run script/net/scapy_pcap_analyzer.py
uv run script/pwn/template_pwntools_example.py
```

## Local Script Area

Owned code and notes live under `script/`. Submodules under `script/` are noted.

- `script/crypto` — crypto helpers, challenge solvers, encoders/decoders
- `script/net` — packet tooling, Scapy experiments, PCAP analysis
- `script/pwn` — pwntools exploits, shellcode work, cIMG helpers, templates
- `script/reverse` — reverse-engineering helpers, angr/r2 scripts
- `script/forensics` — small forensic utilities
- `script/web` — HTTP, session, SQLi, and web exploitation helpers
- `script/utils` — general-purpose utilities, input automation, desktop helpers
- `script/post_exp` — post-exploitation binaries and helpers
- `script/shellcode` — assembly payloads and generated shellcode artifacts
- `script/cheat_sheets` — quick notes and reusable references
- `script/hook` — LD_PRELOAD hooks, ptrace bypass, shellcode runners
- `script/kb-tools` — knowledge base migration and maintenance scripts
- `script/maze` — maze challenge exploits (shellcode injection, GDB scripts)
- `script/dirtyfrag` — [submodule] Dirty COW / race-condition exploit fragments
- `script/pocs` — [submodule] CVE PoC collection

Some scripts are one-off exploit solvers with hard-coded paths, ports, payloads, or challenge assumptions. Read them before reuse.

## Vendored Reference Areas

These directories are mostly third-party material or submodules. Do not edit them as local code unless the task explicitly targets that project.

- `dict/` — wordlists, password dictionaries, and security testing payloads
  - Submodules: SecLists, wister
  - Local: organized by category under passwords/, usernames/, dirs/, subdomains/, payloads/, middleware/, devices/, misc/
  - See [`dict/README.md`](dict/README.md)
- `web/` — third-party exploitation references and offensive tooling (all submodules)
- `reverse/` — reverse-engineering tools, themes, integrations, decompilers (all submodules)
- `forensis/` — forensic signatures, ImHex patterns, file-format specs (all submodules)
- `misc/` — assorted utilities, magic signatures, steg tooling (submodule: qrazybox)
- `pentest/` — [submodule] pentest script collection

## Submodules

The repo tracks many third-party resources as git submodules. Full list (35 total):

**dict**

- `dict/SecLists` — comprehensive wordlist collection
- `dict/wister` — WPA/WPA2 PMKID cracking tool

**web (exploitation & references)**

- `web/PayloadsAllTheThings`
- `web/PEASS-ng` — privilege escalation enumeration
- `web/hacktricks` — hacking techniques wiki
- `web/GTFOBins.github.io` — Unix binary exploitation
- `web/exploit-notes` — exploit development notes
- `web/SSRFmap` — SSRF exploitation framework
- `web/GitTools` — Git repository tools
- `web/antSword` — cross-platform webshell manager
- `web/nc.exe` — netcat for Windows
- `web/nishang` — PowerShell for offensive security
- `web/PowerSploit` — PowerShell exploitation framework
- `web/Priv2Admin` — Windows privilege escalation
- `web/pspy` — Linux process monitoring
- `web/reverse-shell-generator` — reverse shell payload generator
- `web/xsser` — XSS detection and exploitation
- `web/ysoserial` — Java deserialization payloads
- `web/impacket` — Windows protocol exploitation toolkit (SMB, Kerberos, AD secretsdump)

**reverse**

- `reverse/dnSpyEx` — .NET debugger and assembly editor
- `reverse/Ghidra-Themes` — Ghidra IDE themes
- `reverse/ida-pro-mcp` — IDA Pro MCP plugin
- `reverse/ida/long_night` — IDA dark theme
- `reverse/jd-gui` — Java decompiler
- `reverse/ret-sync` — IDA/GDB/Windbg sync

**forensis**

- `forensis/ImHex-Patterns` — ImHex hex editor patterns
- `forensis/kaitai_struct_formats` — binary format definitions
- `forensis/LovelyMem` — memory analysis tools
- `forensis/MemProcFS` — memory process file system
- `forensis/rules` — YARA rules collection
- `forensis/signature-base` — forensic signatures

**misc**

- `misc/steg/qrazybox` — QR code analysis

**Other**

- `pentest` — pentest scripts and tools
- `script/dirtyfrag` — Dirty COW exploit fragments
- `script/pocs` — CVE proof-of-concept collection

Check submodule state before assuming a directory is local code:

```bash
git submodule status --recursive
```

Update all submodules to the commits recorded by this repo:

```bash
git submodule update --init --recursive
```

Update submodules to the latest upstream commits configured in `.gitmodules`:

```bash
git submodule update --remote --recursive
```

After updating submodules, commit the changed submodule pointers in the parent repo if the update should be kept.

## Python Dependencies (script/)

The `script/` directory uses `pyproject.toml` for dependency management (uv-native).
Install with uv:

```bash
cd script
uv sync
```

To upgrade all packages to latest compatible versions:

```bash
uv lock --upgrade && uv sync
```

Dependencies are pinned with `>=` constraints and resolved into `uv.lock`. Key additions beyond the basic CTF toolchain include **gmpy2** (RSA/bigint math), **numpy** (crypto array ops), **pillow** (forensic image analysis), and **impacket** (Windows protocol exploitation, SMB/Kerberos/LDAP).

**Note:** The venv is self-contained inside `script/.venv/`, git-ignored and disposable.

## Maintenance Notes

- Check `git status` before editing. Submodules can be dirty independently of the parent repo.
- `script/pyproject.toml` is the dependency manifest (uv-native, `uv sync` to install).
- `script/.venv/` may exist locally, but it is ignored by git and disposable.
- For Python edits, run a targeted syntax check or execute the touched script when practical.
- For docs-only edits, no test run is required.
- For submodule edits, validate using that subproject's own workflow.
- Keep top-level docs focused on setup, repo layout, and practical usage.
- Submodules are initialized to pinned commits. Run `git submodule update --remote` to pull latest upstream, then commit the updated pointers.

## Included Local References

Useful local notes:

- [`script/cheat_sheets/pwntools_cheatsheet.md`](script/cheat_sheets/pwntools_cheatsheet.md)
- [`script/cheat_sheets/note.md`](script/cheat_sheets/note.md)
- [`script/cheat_sheets/ansi.md`](script/cheat_sheets/ansi.md)
- [`script/crypto/trytodecrypt/README.md`](script/crypto/trytodecrypt/README.md) — trytodecrypt.com solver collection
- [`dict/README.md`](dict/README.md) — wordlist organization
- [`dict/docs/sql-injection-cheatsheet.md`](dict/docs/sql-injection-cheatsheet.md) — SQL injection reference
- [`dict/docs/oracle-cheat-sheet.md`](dict/docs/oracle-cheat-sheet.md) — Oracle hacking reference

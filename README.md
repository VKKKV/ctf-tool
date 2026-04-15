# CTF Toolkit

Personal CTF and security-research workspace with two distinct parts:

- `script/` contains local helper scripts, exploit templates, and notes.
- the rest of the repo is mostly vendored reference material and submodules.

This is not a single packaged application. Treat it as a toolbox repo.

## Getting Started

Clone with submodules if you want the full reference set:

```bash
git clone --recurse-submodules <repo-url>
cd tool
```

If the repo is already cloned:

```bash
git submodule update --init --recursive
```

Set up the local Python environment for `script/`:

```bash
python3 -m venv script/.venv
source script/.venv/bin/activate
pip install -r script/requirements.txt
```

Most custom scripts are then run directly:

```bash
python3 script/<category>/<name>.py
```

Examples:

```bash
python3 script/crypto/xor_cipher_tool.py
python3 script/net/scapy/scapy_pcap_analyzer.py
python3 script/pwn/templates/pwntools_example.py
```

## Repository Layout

### Local Working Area

| Path | Purpose |
| --- | --- |
| `script/crypto` | crypto helpers, CTF solvers, encoders/decoders |
| `script/net` | packet tooling, Scapy experiments, PCAP analysis |
| `script/pwn` | pwntools exploits, shellcode work, templates |
| `script/reverse` | reverse-engineering helpers, angr/r2/cIMG scripts |
| `script/forensics` | small forensic utilities |
| `script/web` | HTTP, session, SQLi, and web exploitation helpers |
| `script/utils` | general-purpose utility scripts |
| `script/post_exp` | post-exploitation binaries and helpers |
| `script/shellcode` | assembly payloads and generated shellcode artifacts |
| `script/cheat_sheets` | notes and quick references |

### Reference Material

| Path | Purpose |
| --- | --- |
| `dict/` | wordlists and password dictionaries |
| `web/` | third-party exploitation references and offensive tooling |
| `reverse/` | reverse-engineering tools, themes, and integrations |
| `forensis/` | forensic signatures, patterns, and formats |
| `misc/` | assorted utilities, magic signatures, and steg tooling |

## Submodules

The repo tracks a large number of third-party resources as submodules, including:

- `dict/SecLists`
- `web/PayloadsAllTheThings`
- `web/PEASS-ng`
- `web/hacktricks`
- `web/GTFOBins.github.io`
- `reverse/dnSpyEx`
- `forensis/ImHex-Patterns`

Do not assume those directories are maintained locally. Check `git submodule status` before editing them.

## Notes For Maintenance

- `script/requirements.txt` is the closest thing to a project dependency manifest.
- `script/.venv/` may exist locally, but it is ignored by git and should be treated as disposable.
- Some scripts contain hard-coded local paths, challenge-specific payloads, or one-off exploit logic. Verify inputs before reuse.
- The top-level repo can be dirty even when your local script changes are clean because submodules track their own state independently.

## Included References

Useful local notes in this repo:

- [script/cheat_sheets/pwntools_cheatsheet.md](/home/kita/ctf/tool/script/cheat_sheets/pwntools_cheatsheet.md)
- [script/cheat_sheets/note.md](/home/kita/ctf/tool/script/cheat_sheets/note.md)
- [script/cheat_sheets/ansi.md](/home/kita/ctf/tool/script/cheat_sheets/ansi.md)

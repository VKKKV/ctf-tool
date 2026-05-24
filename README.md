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

Set up the Python environment for `script/` using **uv**:

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
uv run script/net/scapy/scapy_pcap_analyzer.py
uv run script/pwn/templates/pwntools_example.py
```

## Local Script Area

Owned code and notes live under `script/`.

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

Some scripts are one-off exploit solvers with hard-coded paths, ports, payloads, or challenge assumptions. Read them before reuse.

## Vendored Reference Areas

These directories are mostly third-party material or submodules. Do not edit them as local code unless the task explicitly targets that project.

- `dict/` — wordlists and password dictionaries
- `web/` — third-party exploitation references and offensive tooling
- `reverse/` — reverse-engineering tools, themes, integrations, decompilers
- `forensis/` — forensic signatures, ImHex patterns, file-format specs
- `misc/` — assorted utilities, magic signatures, steg tooling

## Submodules

The repo tracks many third-party resources as git submodules, including:

- `dict/SecLists`
- `web/PayloadsAllTheThings`
- `web/PEASS-ng`
- `web/hacktricks`
- `web/GTFOBins.github.io`
- `web/exploit-notes`
- `reverse/dnSpyEx`
- `reverse/ida-pro-mcp`
- `reverse/ret-sync`
- `forensis/ImHex-Patterns`
- `forensis/rules`
- `forensis/signature-base`

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

The full locked dependency list is in `script/pyproject.toml` (`[project] dependencies`).

**Note:** The venv is self-contained — these packages are installed inside `script/.venv/`, not globally. Most are also available as Arch packages (see `python-<name>`), but the venv ensures consistent versions regardless of the host distro.

## Maintenance Notes

- Check `git status` before editing. Submodules can be dirty independently of the parent repo.
- `script/pyproject.toml` is the dependency manifest (uv-native, `uv sync` to install).
- `script/.venv/` may exist locally, but it is ignored by git and disposable.
- For Python edits, run a targeted syntax check or execute the touched script when practical.
- For docs-only edits, no test run is required.
- For submodule edits, validate using that subproject's own workflow.
- Keep top-level docs focused on setup, repo layout, and practical usage.

## Included Local References

Useful local notes:

- [`script/cheat_sheets/pwntools_cheatsheet.md`](script/cheat_sheets/pwntools_cheatsheet.md)
- [`script/cheat_sheets/note.md`](script/cheat_sheets/note.md)
- [`script/cheat_sheets/ansi.md`](script/cheat_sheets/ansi.md)

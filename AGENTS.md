# AGENTS.md

## Repo Intent

This repository is a personal CTF/security toolbox, not a single deployable application.

- primary owned code lives under `script/`
- most other top-level directories are vendored tools, notes, or git submodules

Prefer changing local scripts and top-level docs unless the task explicitly targets a vendored project.

## Working Rules

- Inspect `git status` before editing; submodules are often dirty independently of local work.
- Avoid modifying submodule content unless the user asks for it.
- Treat challenge-specific scripts as disposable utilities unless there is an obvious shared abstraction to extract.
- Many scripts are one-off exploit solvers with hard-coded paths, ports, or payloads; preserve that style unless the task is specifically to generalize them.

## Useful Paths

- `script/crypto` - crypto helpers and challenge solves
- `script/net` - Scapy and packet-analysis helpers
- `script/pwn` - pwntools exploits, templates, shellcode-oriented scripts
- `script/reverse` - angr, radare2, cIMG, and reversing helpers
- `script/web` - web exploitation helpers
- `script/utils` - general utility scripts
- `script/cheat_sheets` - local notes worth reusing before adding new docs

## Setup

Typical local environment:

```bash
python3 -m venv script/.venv
source script/.venv/bin/activate
pip install -r script/requirements.txt
```

Initialize submodules when needed:

```bash
git submodule update --init --recursive
```

## Validation

There is no single project-wide test suite.

- for Python edits, prefer targeted syntax checks or running the specific script
- for docs-only edits, no test run is required
- for submodule edits, validate using that subproject's own workflow

## Documentation

Keep top-level documentation focused on:

- how to set up the local script environment
- which directories are owned locally versus vendored
- practical usage examples instead of exhaustive inventories

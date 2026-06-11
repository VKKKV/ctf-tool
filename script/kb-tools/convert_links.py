#!/usr/bin/env python3
"""Convert `[TITLE](OLD_PATH)` links to `[[NEW_PATH|TITLE]]` wikilinks in index-2025.md."""

import re
import os

MAPPING_FILE = "/tmp/mapping.tsv"
INDEX_FILE = "/home/kita/code/knowledge/notes/wechat-public-account/index-2025.md"

# Build mapping dict: OLD_PATH -> NEW_PATH
mapping = {}
with open(MAPPING_FILE, "r", encoding="utf-8") as f:
    for line in f:
        line = line.strip()
        if not line:
            continue
        parts = line.split("\t", 1)
        if len(parts) == 2:
            old_path, new_path = parts
            mapping[old_path] = new_path
        else:
            print(f"WARNING: Skipping malformed mapping line: {line}")

print(f"Loaded {len(mapping)} mappings from {MAPPING_FILE}")

# Read the index file
with open(INDEX_FILE, "r", encoding="utf-8") as f:
    lines = f.readlines()

print(f"Read {len(lines)} lines from {INDEX_FILE}")

# Pattern: lines starting with "- DATE [TITLE](OLD_PATH) — AUTHOR"
# More specifically: ^- \d{4}-\d{2}-\d{2} \[TITLE\]\(OLD_PATH\) — AUTHOR
line_pattern = re.compile(r'^(- \d{4}-\d{2}-\d{2} )\[([^\]]+)\]\(([^)]+)\)( — .*)$')

converted = 0
failed = 0
new_lines = []

for i, line in enumerate(lines):
    m = line_pattern.match(line)
    if m:
        prefix = m.group(1)   # "- 2025-01-11 "
        title = m.group(2)    # "札记 ｜ 余命……？"
        old_path = m.group(3) # "articles/2025/2025-01-11-2247484583-1.md"
        suffix = m.group(4)   # " — 单字一兔"

        if old_path in mapping:
            new_path = mapping[old_path]
            new_line = f"{prefix}[[{new_path}|{title}]]{suffix}\n"
            converted += 1
        else:
            # Try with leading ./ or other variations
            # The old_path in the index doesn't have a leading ./
            # Let's also try stripping/adding prefixes
            alt_path = old_path
            if alt_path in mapping:
                new_path = mapping[alt_path]
                new_line = f"{prefix}[[{new_path}|{title}]]{suffix}\n"
                converted += 1
            else:
                print(f"WARNING: No mapping found for OLD_PATH: {old_path}")
                print(f"  Line {i+1}: {line.rstrip()}")
                failed += 1
                new_line = line  # keep unchanged
        new_lines.append(new_line)
    else:
        # Not an article entry line, keep as-is
        new_lines.append(line)

# Write back
with open(INDEX_FILE, "w", encoding="utf-8") as f:
    f.writelines(new_lines)

print(f"\nDone! Converted: {converted}, Failed (no mapping): {failed}")

#!/usr/bin/env python3
"""
Tidy all WeChat articles in the 2022 directory:
  - Remove absolute path from YAML frontmatter
  - Add tags, parent, topic, decision to YAML
  - Remove absolute path from body
  - Add wikilink footer
"""

import json
import os
import re
import sys

ARTICLES_DIR = "/home/kita/code/knowledge/notes/wechat-public-account/articles/2022"
COVERAGE_FILE = "/tmp/coverage_lookup.json"

# Load coverage lookup
with open(COVERAGE_FILE, "r", encoding="utf-8") as f:
    coverage = json.load(f)

# Get all .md files
files = sorted(os.listdir(ARTICLES_DIR))
files = [f for f in files if f.endswith(".md")]

total = len(files)
coverage_hits = 0
errors = []

for fname in files:
    fpath = os.path.join(ARTICLES_DIR, fname)
    lookup_key = f"articles/2022/{fname}"

    try:
        with open(fpath, "r", encoding="utf-8") as f:
            content = f.read()
    except Exception as e:
        errors.append((fname, f"read error: {e}"))
        continue

    lines = content.split("\n")

    # ---------------------------------------------------------------
    # 1. Locate YAML frontmatter boundaries
    # ---------------------------------------------------------------
    # Frontmatter should start with '---' on line 0, end with '---'
    if not lines or lines[0].strip() != "---":
        errors.append((fname, "no opening ---"))
        continue

    # Find closing '---'
    end_yaml = None
    for i in range(1, len(lines)):
        if lines[i].strip() == "---":
            end_yaml = i
            break

    if end_yaml is None:
        errors.append((fname, "no closing ---"))
        continue

    # ---------------------------------------------------------------
    # 2. Process YAML lines (between lines 1 and end_yaml-1 inclusive)
    # ---------------------------------------------------------------
    yaml_lines = lines[1:end_yaml]
    body_lines = lines[end_yaml:]  # includes the closing ---

    # Remove source_file line from YAML
    cleaned_yaml = []
    for line in yaml_lines:
        if line.strip().startswith("source_file:"):
            continue  # remove this line
        cleaned_yaml.append(line)

    # Prepare new fields to insert (before closing ---)
    new_fields = []
    new_fields.append("tags: [wechat-archive]")
    new_fields.append("parent: [[index-2022]]")

    # Look up coverage data
    entry = coverage.get(lookup_key)
    if entry:
        coverage_hits += 1
        topic = entry.get("topic", "")
        if topic and topic.strip():
            new_fields.append(f"topic: {topic}")
        decision = entry.get("decision")
        if decision:
            new_fields.append(f"decision: {decision}")

    # Reconstruct the file:
    # opening ---
    # cleaned YAML lines
    # new fields
    # closing ---
    # body (after closing ---)
    #
    # BUT: new fields go BEFORE the closing ---, so we insert them
    # into the yaml section before the body lines.

    out_lines = []
    out_lines.append("---")
    out_lines.extend(cleaned_yaml)
    out_lines.extend(new_fields)
    out_lines.append("---")

    # ---------------------------------------------------------------
    # 3. Process body (lines after closing ---)
    # ---------------------------------------------------------------
    # body_lines[0] is the closing '---' itself, skip it
    body = body_lines[1:] if len(body_lines) > 1 else []

    # Remove the import source line from body
    cleaned_body = []
    for line in body:
        if line.strip().startswith("- 导入来源:") and "/home/kita/Downloads/微信公众号文章.json" in line:
            continue  # remove
        cleaned_body.append(line)

    # Add body content
    out_lines.extend(cleaned_body)

    # Ensure there's a trailing newline before the footer
    if out_lines and out_lines[-1] != "":
        out_lines.append("")

    # Add footer wikilink
    out_lines.append("[[index-2022|← 返回索引]]")

    new_content = "\n".join(out_lines)

    try:
        with open(fpath, "w", encoding="utf-8") as f:
            f.write(new_content)
    except Exception as e:
        errors.append((fname, f"write error: {e}"))
        continue

    print(f"  OK  {fname}")

# Summary
print(f"\n{'='*60}")
print(f"Total files processed: {total}")
print(f"Files with coverage data: {coverage_hits}")
print(f"Errors: {len(errors)}")
if errors:
    print(f"{'='*60}")
    for fname, reason in errors:
        print(f"  ERROR {fname}: {reason}")

sys.exit(0 if not errors else 1)

#!/usr/bin/env python3
"""
Tidy all WeChat articles in the 2023 directory:
- Clean up YAML frontmatter (remove source_file path)
- Add tags, parent wikilink, and optional topic/decision from coverage lookup
- Remove absolute import path from body
- Add return wikilink at end
"""
import json
import os
import re
import sys

ARTICLES_DIR = "/home/kita/code/knowledge/notes/wechat-public-account/articles/2023"
COVERAGE_FILE = "/tmp/coverage_lookup.json"

# Load coverage data
with open(COVERAGE_FILE, "r", encoding="utf-8") as f:
    coverage = json.load(f)

# Get all .md files in the 2023 directory
files = sorted([f for f in os.listdir(ARTICLES_DIR) if f.endswith(".md")])

stats = {
    "total": len(files),
    "with_coverage": 0,
    "with_topic": 0,
    "with_decision": 0,
    "errors": 0,
    "error_files": [],
}

for filename in files:
    filepath = os.path.join(ARTICLES_DIR, filename)
    coverage_key = f"articles/2023/{filename}"

    try:
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()
    except Exception as e:
        print(f"ERROR reading {filename}: {e}")
        stats["errors"] += 1
        stats["error_files"].append(filename)
        continue

    # Check for YAML frontmatter
    if not content.startswith("---\n"):
        print(f"WARNING: {filename} does not start with YAML frontmatter. Skipping.")
        stats["errors"] += 1
        stats["error_files"].append(filename)
        continue

    # Split into frontmatter and body
    # Find the closing ---
    end_yaml = content.find("\n---\n", 4)
    if end_yaml == -1:
        print(f"WARNING: {filename} has no closing YAML '---'. Skipping.")
        stats["errors"] += 1
        stats["error_files"].append(filename)
        continue

    yaml_block = content[4:end_yaml]  # content between the opening and closing ---
    body = content[end_yaml + 5:]     # everything after the closing ---\n

    # --- Process YAML ---
    lines = yaml_block.split("\n")
    new_lines = []
    for line in lines:
        # Remove source_file line
        if line.strip().startswith("source_file:"):
            continue
        new_lines.append(line)

    # Build new fields to add
    additions = []

    # tags and parent always
    additions.append("tags: [wechat-archive]")
    additions.append("parent: [[index-2023]]")

    # Look up coverage data
    if coverage_key in coverage:
        stats["with_coverage"] += 1
        entry = coverage[coverage_key]

        # topic field
        topic = entry.get("topic", "")
        if topic and topic.strip():
            additions.append(f"topic: [{topic}]")
            stats["with_topic"] += 1

        # decision field
        if "decision" in entry:
            decision = entry["decision"]
            additions.append(f"decision: {decision}")
            stats["with_decision"] += 1

    # Append additions before the closing ---
    for add_line in additions:
        new_lines.append(add_line)

    new_yaml = "\n".join(new_lines)

    # --- Process Body ---
    # Remove the "导入来源" absolute path line
    body_lines = body.split("\n")
    cleaned_body_lines = []
    for line in body_lines:
        if line.strip().startswith("- 导入来源:") or "导入来源:" in line and "/home/kita/Downloads/" in line:
            continue
        cleaned_body_lines.append(line)
    cleaned_body = "\n".join(cleaned_body_lines)

    # Ensure the body ends with exactly one newline, then append the wikilink
    cleaned_body = cleaned_body.rstrip("\n") + "\n\n[[index-2023|← 返回索引]]\n"

    # --- Reassemble ---
    new_content = "---\n" + new_yaml + "\n---\n" + cleaned_body

    try:
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(new_content)
        print(f"OK: {filename}")
    except Exception as e:
        print(f"ERROR writing {filename}: {e}")
        stats["errors"] += 1
        stats["error_files"].append(filename)

# --- Report ---
print("\n" + "=" * 60)
print("TIDY COMPLETE - 2023 WeChat Articles")
print("=" * 60)
print(f"Total files processed: {stats['total']}")
print(f"Files with coverage data: {stats['with_coverage']} / {stats['total']}")
print(f"  - with topic field added: {stats['with_topic']}")
print(f"  - with decision field added: {stats['with_decision']}")
print(f"Errors: {stats['errors']}")
if stats["error_files"]:
    for ef in stats["error_files"]:
        print(f"  - {ef}")

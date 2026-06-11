#!/usr/bin/env python3
"""
Tidy all WeChat articles in the 2026 directory - IDEMPOTENT v2.
- Clean up YAML frontmatter (remove source_file, ensure tags/parent/topic/decision)
- Remove absolute path line from body
- Add backlink wikilink at end
"""

import json
import os
import re

KB_ROOT = "/home/kita/code/knowledge"
ARTICLES_DIR = os.path.join(
    KB_ROOT, "notes", "wechat-public-account", "articles", "2026"
)
COVERAGE_FILE = "/tmp/coverage_lookup.json"

# Load coverage lookup
with open(COVERAGE_FILE, "r", encoding="utf-8") as f:
    coverage = json.load(f)

# Normalize key for matching (handle JSON-escaped quotes)
coverage_norm = {}
for k, v in coverage.items():
    coverage_norm[k.replace('\\"', '"')] = v

stats = {
    "processed": 0,
    "errors": [],
    "with_coverage_topic": 0,
    "with_coverage_decision": 0,
}

entries = sorted(os.listdir(ARTICLES_DIR))
md_files = [f for f in entries if f.endswith(".md")]

print(f"Found {len(md_files)} .md files in {ARTICLES_DIR}")

# Fields we manage (will be removed and re-added)
MANAGED_FIELDS = {"source_file", "tags", "parent", "topic", "decision"}

for filename in md_files:
    filepath = os.path.join(ARTICLES_DIR, filename)
    lookup_key = f"articles/2026/{filename}"

    try:
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()
    except Exception as e:
        stats["errors"].append(f"READ_ERROR {filename}: {e}")
        continue

    orig_content = content

    # ---------------------------------------------------------------
    # 1. YAML FRONTMATTER edits - idempotent
    # ---------------------------------------------------------------
    fm_match = re.match(r"^---\n(.*?)\n---", content, re.DOTALL)
    if not fm_match:
        stats["errors"].append(f"NO_FM {filename}: no frontmatter found")
        continue

    fm_text = fm_match.group(1)
    fm_end = fm_match.end()

    # Parse existing frontmatter lines, excluding managed fields
    remaining_lines = []
    for line in fm_text.split("\n"):
        field_name_match = re.match(r"^(\w+)\s*:", line)
        if field_name_match and field_name_match.group(1) in MANAGED_FIELDS:
            continue
        remaining_lines.append(line)

    # Build new fields from coverage
    new_fields = [
        "tags: [wechat-archive]",
        "parent: [[index-2026]]",
    ]

    cove_entry = coverage.get(lookup_key) or coverage_norm.get(lookup_key)
    if cove_entry is not None:
        topic_val = cove_entry.get("topic", "")
        if topic_val:
            # YAML plain scalar: safe chars are / _ - letters. Quote if needed.
            if any(c in topic_val for c in [":", "#", "[", "]", "{", "}", ",", "&", "*", "!", "|", ">", "'", "\""]):
                new_fields.append(f'topic: "{topic_val}"')
            else:
                new_fields.append(f"topic: {topic_val}")
            stats["with_coverage_topic"] += 1
        decision_val = cove_entry.get("decision")
        if decision_val is not None:
            new_fields.append(f"decision: {decision_val}")
            stats["with_coverage_decision"] += 1

    # Reconstruct frontmatter
    new_fm_text = "\n".join(remaining_lines + [""] + new_fields)
    new_fm = f"---\n{new_fm_text}\n---"

    content = new_fm + content[fm_end:]

    # ---------------------------------------------------------------
    # 2. BODY edits
    # ---------------------------------------------------------------
    # Remove 导入来源 line
    content = re.sub(
        r'^-\s*导入来源:\s*`/home/kita/Downloads/微信公众号文章\.json`\s*\n?',
        "",
        content,
        flags=re.MULTILINE,
    )

    # Remove ALL existing backlinks (they may have been duplicated)
    content = content.replace("[[index-2026|← 返回索引]]", "")

    # Clean up excessive blank lines
    content = re.sub(r'\n{3,}', '\n\n', content)

    # Add single backlink at end
    content = content.rstrip("\n") + "\n\n[[index-2026|← 返回索引]]\n"

    # ---------------------------------------------------------------
    # 3. Write back if changed
    # ---------------------------------------------------------------
    if content != orig_content:
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)
        stats["processed"] += 1
    else:
        stats["processed"] += 1

# Summary
print("\n=== RESULTS ===")
print(f"Files processed: {stats['processed']}")
print(f"Files with coverage topic: {stats['with_coverage_topic']}")
print(f"Files with coverage decision: {stats['with_coverage_decision']}")
if stats["errors"]:
    print(f"Errors ({len(stats['errors'])}):")
    for err in stats["errors"]:
        print(f"  - {err}")
else:
    print("Errors: 0")

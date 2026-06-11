# Dictionary Collection

Reorganized wordlists for CTF and security testing. Original sources:
`MyDict/`, `PasswordDic/`, and `逸尘的字典/` have been merged by category.

## Structure

```
passwords/       — Password wordlists (rockyou, common, cn-weak, services)
usernames/       — Username/account lists (common, cn-names, mail, phone)
dirs/            — Directory brute-force lists by tech stack
subdomains/      — Subdomain enumeration lists
payloads/        — Security testing payloads (SQLi, XSS, RCE, LFI, etc.)
middleware/      — Middleware default credentials & paths
devices/         — Security product default credentials
misc/            — Extension lists, user agents, generic fuzz
docs/            — Reference PDFs, XLSX, images (non-dict)
```

## Notes

- `rockyou.txt` and `cn-weak.txt` are large reference files (134MB / 41MB), kept as-is
- Small files (< 10K lines) are merged and deduplicated within each category
- SecLists and wister are git submodules, not covered here
- Original directories (MyDict/, PasswordDic/, 逸尘的字典/) kept for backward compat

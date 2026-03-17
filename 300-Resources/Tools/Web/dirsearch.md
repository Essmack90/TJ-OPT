---
tags: [tool, web, fuzzer]
tool: "dirsearch"
category: "Web"
installed: true
phase: [recon, discovery]
---

# dirsearch - Directory Brute Forcer

## Tool Overview
**Purpose:** Directory brute forcing with multiple extensions and recursion
**Location:** `~/tools/web/dirsearch/dirsearch.py`

## When to Use
- Deep directory enumeration
- Finding hidden files and directories
- Recursive scanning

## How to Use It
python3 ~/tools/web/dirsearch/dirsearch.py -u https://target.com -e php,html,txt

## Related Tools
- ffuf
- gobuster
- feroxbuster

---
tags: [tool, web, fuzzer]
tool: "feroxbuster"
category: "Web"
installed: true
phase: [recon, discovery]
---

# feroxbuster - Recursive Content Discovery

## Tool Overview
**Purpose:** Fast, recursive content discovery written in Rust
**Location:** `which feroxbuster`

## When to Use
- Recursive directory scanning
- When ffuf/gobuster miss something
- Need automatic recursion

## How to Use It
feroxbuster -u https://target.com -w wordlist.txt

## Related Tools
- ffuf
- gobuster
- dirsearch

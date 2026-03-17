---
tags: [tool, web, fuzzer]
tool: "wfuzz"
category: "Web"
installed: true
phase: [recon, exploitation]
---

# wfuzz - Web Application Brute Forcer

## Tool Overview
**Purpose:** Web application brute forcing, POST parameter fuzzing
**Location:** `which wfuzz`

## When to Use
- Authentication bypass testing
- Parameter fuzzing
- Hidden content discovery

## How to Use It
wfuzz -w wordlist.txt -d "user=FUZZ&pass=FUZZ" https://target.com/login

## Related Tools
- ffuf
- gobuster

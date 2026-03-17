---
tags: [tool, web, fuzzer]
tool: "ffuf"
category: "Web"
installed: true
phase: [recon, discovery]
---

# ffuf - Fast Web Fuzzer

## Tool Overview
**Purpose:** Directory/file fuzzing, parameter fuzzing, vhost discovery
**Location:** `which ffuf`
**Version:** `ffuf -V`

## When to Use
- Directory brute forcing to find hidden paths
- Parameter fuzzing to discover hidden inputs
- Virtual host discovery
- POST parameter fuzzing
- When you need SPEED (written in Go)

## Why This Tool
**Strengths:**
- Fastest fuzzer available
- Recursive scanning built-in
- Filter by status codes, size, words, lines
- Can fuzz multiple positions simultaneously
- Supports mutex and matcher conditions

## How to Use It

### Basic Directory Fuzzing
ffuf -w /usr/share/wordlists/dirb/common.txt -u https://target.com/FUZZ

### File Extension Fuzzing
ffuf -w wordlist.txt -u https://target.com/FUZZ -e .php,.html,.txt

### Virtual Host Discovery
ffuf -w subdomains.txt -H "Host: FUZZ.target.com" -u https://target.com

### Common Options
- `-w` : Wordlist path
- `-u` : Target URL (FUZZ placeholder)
- `-e` : File extensions
- `-H` : Custom headers
- `-X` : HTTP method
- `-d` : POST data
- `-fc` : Filter by status codes
- `-fs` : Filter by response size
- `-t` : Threads (default 40)

### Real Example
ffuf -w /usr/share/seclists/Discovery/Web-Content/common.txt -u https://10.10.10.10/FUZZ -fc 403,404

## Related Tools
- gobuster
- dirb
- wfuzz
- feroxbuster

## Resources
- [ffuf GitHub](https://github.com/ffuf/ffuf)

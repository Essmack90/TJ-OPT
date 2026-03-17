---
tags: [tool, web, fuzzer, dns]
tool: "gobuster"
category: "Web"
installed: true
phase: [recon, discovery]
---

# gobuster - Directory/File/DNS Brute Forcer

## Tool Overview
**Purpose:** Multi-purpose brute forcing for directories, DNS subdomains, vhosts, and S3 buckets
**Location:** `which gobuster`

## When to Use
- Directory/file brute forcing (dir mode)
- DNS subdomain enumeration (dns mode)
- Virtual host discovery (vhost mode)
- S3 bucket discovery (s3 mode)

## Why This Tool
**Strengths:**
- Multi-mode (dir, dns, vhost, s3, fuzz)
- Good balance of speed and reliability
- Clear output with status codes and sizes
- Wildcard handling for DNS

## How to Use It

### Directory Mode
gobuster dir -u https://target.com -w /usr/share/wordlists/dirb/common.txt

### DNS Subdomain Enumeration
gobuster dns -d target.com -w /usr/share/seclists/Discovery/DNS/subdomains-top1million-5000.txt

### Virtual Host Discovery
gobuster vhost -u https://target.com -w subdomains.txt

### Common Options
- `-x` : File extensions (dir mode)
- `-r` : Use custom DNS resolver (dns mode)
- `-t` : Threads (default 10)
- `-o` : Output file

## Related Tools
- ffuf
- dirb
- wfuzz

## Resources
- [gobuster GitHub](https://github.com/OJ/gobuster)

---
tags: [tool, web, parameter]
tool: "arjun"
category: "Web"
installed: true
phase: [recon]
---

# arjun - HTTP Parameter Discovery

## Tool Overview
**Purpose:** Finds hidden HTTP parameters
**Location:** `which arjun`

## When to Use
- Finding undocumented parameters
- Parameter enumeration for bug bounty
- Discovering hidden inputs

## How to Use It

### Basic Usage
arjun -u https://target.com/page

### With Custom Wordlist
arjun -u https://target.com/page -w /path/to/wordlist

## Related Tools
- ffuf
- parameth

## Resources
- [arjun GitHub](https://github.com/s0md3v/Arjun)

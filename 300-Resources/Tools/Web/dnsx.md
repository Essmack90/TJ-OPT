---
tags: [tool, dns, recon]
tool: "dnsx"
category: "Web"
installed: true
phase: [recon]
---

# dnsx - DNS Toolkit

## Tool Overview
**Purpose:** Fast DNS query tool
**Location:** `which dnsx`

## When to Use
- DNS enumeration
- A/AAAA/CNAME record lookups
- Wildcard detection

## How to Use It
echo "target.com" | dnsx -a -cname -resp

## Related Tools
- dig
- nslookup

---
tags: [tool, osint, subdomain]
tool: "sublist3r"
category: "OSINT"
installed: true
phase: [recon]
---

# sublist3r - Subdomain Discovery

## Tool Overview
Purpose: Fast subdomain enumeration using search engines
Location: /usr/bin/sublist3r

## When to Use
- Finding subdomains for a domain
- Initial web application recon

## How to Use It

Basic Scan:
sublist3r -d example.com

Verbose Output:
sublist3r -d example.com -v

Save Results:
sublist3r -d example.com -o subdomains.txt

Use Specific Engines:
sublist3r -d example.com -e google,bing,yahoo

## Related Tools
theharvester, amass

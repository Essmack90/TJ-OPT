---
tags: [tool, web, prober]
tool: "httpx"
category: "Web"
installed: true
phase: [recon]
---

# httpx - HTTP Prober

## Tool Overview
**Purpose:** Fast HTTP probe to check live hosts, tech detection, screenshot
**Location:** `which httpx`

## When to Use
- Probing a list of subdomains to find live hosts
- Technology stack detection
- Taking screenshots of multiple sites
- Extracting titles and status codes

## How to Use It

### Probe Subdomains
cat subdomains.txt | httpx -title -tech-detect -status-code

### Screenshot Websites
cat urls.txt | httpx -screenshot

## Related Tools
- nuclei
- katana
- aquatone

## Resources
- [httpx GitHub](https://github.com/projectdiscovery/httpx)

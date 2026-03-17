---
tags: [tool, web, crawler]
tool: "katana"
category: "Web"
installed: true
phase: [recon, discovery]
---

# katana - Fast Web Crawler

## Tool Overview
**Purpose:** Fast web crawler for endpoint discovery, JS parsing, form extraction
**Location:** `which katana`

## When to Use
- Crawling websites to discover all endpoints
- Extracting JavaScript files for analysis
- Finding hidden forms and parameters
- Mapping out site structure

## How to Use It

### Basic Crawl
katana -u https://target.com

### Crawl with JavaScript Parsing
katana -u https://target.com -jc

### Crawl and Output to File
katana -u https://target.com -o urls.txt

## Related Tools
- httpx
- waybackurls
- gau

## Resources
- [katana GitHub](https://github.com/projectdiscovery/katana)

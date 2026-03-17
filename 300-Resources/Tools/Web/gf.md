---
tags: [tool, web, grep]
tool: "gf"
category: "Web"
installed: true
phase: [recon]
---

# gf - Grep Wrapper for Pattern Matching

## Tool Overview
**Purpose:** grep wrapper for common attack patterns
**Location:** `which gf`

## When to Use
- Finding XSS/SSRF/SQLi patterns in URLs
- Extracting interesting endpoints
- Pattern matching on collected data

## How to Use It
cat urls.txt | gf xss

## Related Tools
- unfurl
- grep

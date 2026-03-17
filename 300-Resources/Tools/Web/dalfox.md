---
tags: [tool, web, xss]
tool: "dalfox"
category: "Web"
installed: true
phase: [exploitation]
---

# dalfox - XSS Scanner

## Tool Overview
**Purpose:** Advanced XSS scanning and parameter analysis
**Location:** `which dalfox`

## When to Use
- Scanning for XSS vulnerabilities
- Testing parameters for XSS
- DOM-based XSS detection
- Blind XSS payloads

## How to Use It

### Scan Single URL
dalfox url https://target.com/page\?param\=test

### Scan with Custom Payloads
dalfox url https://target.com/page\?param\=test --custom-payload /path/to/payloads

## Related Tools
- xsstrike
- xsser

## Resources
- [dalfox GitHub](https://github.com/hahwul/dalfox)

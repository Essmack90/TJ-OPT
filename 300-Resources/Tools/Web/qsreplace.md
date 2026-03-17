---
tags: [tool, web, url]
tool: "qsreplace"
category: "Web"
installed: true
phase: [exploitation]
---

# qsreplace - Query String Replacer

## Tool Overview
**Purpose:** Replace query strings in URLs
**Location:** `which qsreplace`

## When to Use
- Testing parameter injection
- Replacing values in URL lists
- Preparing payloads

## How to Use It
cat urls.txt | qsreplace "payload"

## Related Tools
- unfurl
- ffuf

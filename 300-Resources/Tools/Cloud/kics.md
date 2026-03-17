---
tags: [tool, cloud, iac, security]
tool: "kics"
category: "Cloud"
installed: true
phase: [analysis, security]
---

# KICS - Keeping Infrastructure as Code Secure

## Tool Overview
Purpose: Static analysis for Infrastructure as Code
Location: /usr/local/bin/kics

## When to Use
- Multi-platform IaC scanning
- Security misconfiguration detection
- Compliance validation

## How to Use It

Scan directory:
kics scan -p .

Scan with output:
kics scan -p . -o results.json

## Related Tools
checkov, tfsec

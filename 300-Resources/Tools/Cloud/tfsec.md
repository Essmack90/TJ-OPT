---
tags: [tool, cloud, terraform, security]
tool: "tfsec"
category: "Cloud"
installed: true
phase: [analysis, security]
---

# tfsec - Terraform Security Scanner

## Tool Overview
Purpose: Static analysis for Terraform code
Location: /usr/local/bin/tfsec

## When to Use
- Terraform security checks
- Misconfiguration detection
- Compliance validation

## How to Use It

Scan directory:
tfsec .

Scan specific files:
tfsec main.tf

Output JSON:
tfsec . --format json

## Related Tools
checkov, terrascan

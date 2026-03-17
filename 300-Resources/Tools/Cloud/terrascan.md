---
tags: [tool, cloud, iac, security]
tool: "terrascan"
category: "Cloud"
installed: true
phase: [analysis, security]
---

# Terrascan - IaC Security Scanner

## Tool Overview
Purpose: Static code analyzer for Infrastructure as Code
Location: /home/kali/.local/bin/terrascan

## When to Use
- Terraform security scanning
- Kubernetes manifest validation
- Compliance checking

## How to Use It

Scan directory:
terrascan scan -d .

Scan with policy:
terrascan scan -d . -p ./custom-policies

## Related Tools
checkov, tfsec

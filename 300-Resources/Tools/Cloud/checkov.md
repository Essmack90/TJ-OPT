---
tags: [tool, cloud, iac, security]
tool: "checkov"
category: "Cloud"
installed: true
phase: [analysis, security]
---

# Checkov - IaC Security Scanner

## Tool Overview
Purpose: Static analysis for Infrastructure as Code
Location: /home/kali/.local/bin/checkov

## When to Use
- Terraform security scanning
- CloudFormation validation
- Kubernetes manifest analysis
- Dockerfile checking

## How to Use It

Scan directory:
checkov -d .

Scan specific file:
checkov -f main.tf

Output format:
checkov -d . --output junitxml

## Related Tools
tfsec, terrascan

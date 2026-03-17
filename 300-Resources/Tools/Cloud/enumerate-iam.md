---
tags: [tool, cloud, aws, enumeration]
tool: "enumerate-iam"
category: "Cloud"
installed: true
phase: [recon, enumeration]
---

# enumerate-iam - AWS IAM Enumeration

## Tool Overview
Purpose: Enumerate IAM permissions from AWS keys
Location: /home/kali/.local/bin/enumerate-iam

## When to Use
- Test AWS access keys
- Determine IAM permissions
- Privilege escalation recon

## How to Use It

Basic enumeration:
enumerate-iam --access-key KEY --secret-key SECRET

Verbose output:
enumerate-iam --access-key KEY --secret-key SECRET --verbose

## Related Tools
aws-cli, pacu

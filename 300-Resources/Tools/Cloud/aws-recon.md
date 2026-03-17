---
tags: [tool, cloud, aws, recon]
tool: "aws-recon"
category: "Cloud"
installed: true
phase: [recon]
---

# aws-recon - AWS Resource Enumeration

## Tool Overview
Purpose: Enumerate AWS resources across services
Location: /home/kali/go/bin/aws-recon

## When to Use
- Comprehensive AWS resource discovery
- Service enumeration
- Cloud asset inventory

## How to Use It

Basic scan:
aws-recon

Specify services:
aws-recon --services s3,ec2,iam

Output to file:
aws-recon --output file.json

## Related Tools
aws-cli, pacu

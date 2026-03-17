---
tags: [tool, cloud, aws, ebs]
tool: "dufflebag"
category: "Cloud"
installed: true
phase: [recon, data-leak]
---

# Dufflebag - Search EBS Snapshots

## Tool Overview
Purpose: Search public EBS snapshots for secrets
Location: /usr/bin/dufflebag

## When to Use
- Finding exposed data in EBS snapshots
- Cloud data leak discovery
- Secrets enumeration

## How to Use It

Run search:
dufflebag --access-key KEY --secret-key SECRET --search-terms passwords.txt

## Related Tools
aws-cli, s3scanner

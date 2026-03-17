---
tags: [tool, cloud, aws, security]
tool: "prowler"
category: "Cloud"
installed: true
phase: [audit, security]
---

# Prowler - AWS Security Tool

## Tool Overview
Purpose: AWS security assessment and hardening tool
Location: /home/kali/.local/bin/prowler

## When to Use
- AWS security auditing
- Compliance checks (CIS benchmarks)
- Finding misconfigurations

## How to Use It

Basic scan:
prowler

Scan specific region:
prowler -r us-east-1

Output to CSV:
prowler -M csv

## Related Tools
scoutsuite, cloudsploit

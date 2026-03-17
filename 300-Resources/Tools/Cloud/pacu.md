---
tags: [tool, cloud, aws, exploitation]
tool: "pacu"
category: "Cloud"
installed: true
phase: [exploitation]
---

# Pacu - AWS Exploitation Framework

## Tool Overview
Purpose: AWS exploitation framework (like Metasploit for AWS)
Location: /home/kali/.local/bin/pacu

## When to Use
- AWS penetration testing
- Privilege escalation
- Post-exploitation

## How to Use It

Start Pacu:
pacu

List modules:
list

Use a module:
use iam__privesc_scan

Set options:
set region us-east-1
run

## Key Modules
- iam__privesc_scan - Find privilege escalation paths
- iam__bruteforce_permissions - Enumerate permissions
- ec2__download_userdata - Extract EC2 user data

## Related Tools
aws-cli, enumerate-iam

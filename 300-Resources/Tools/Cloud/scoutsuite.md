---
tags: [tool, cloud, multi-cloud, security]
tool: "scoutsuite"
category: "Cloud"
installed: true
phase: [audit, security]
---

# ScoutSuite - Multi-Cloud Security Auditing

## Tool Overview
Purpose: Multi-cloud security auditing tool
Location: /home/kali/.local/bin/scout

## When to Use
- AWS/Azure/GCP security assessment
- Finding cloud misconfigurations
- Security compliance checks

## How to Use It

AWS scan:
scout aws

Azure scan:
scout azure

GCP scan:
scout gcp

Generate HTML report:
scout aws --report-dir ./reports

## Related Tools
prowler, cloudsploit

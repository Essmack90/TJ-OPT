---
tags: [tool, cloud, multi-cloud, security]
tool: "cloudsploit"
category: "Cloud"
installed: true
phase: [audit, security]
---

# Cloudsploit - Cloud Security Scanning

## Tool Overview
Purpose: Cloud security misconfiguration scanner
Location: ~/tools/cloud/cloudsploit

## When to Use
- AWS/Azure/GCP security scanning
- Finding exposed resources
- Compliance checking

## How to Use It

Run scan:
cd ~/tools/cloud/cloudsploit
node index.js

With AWS keys:
node index.js --config ./config.js

## Related Tools
prowler, scoutsuite

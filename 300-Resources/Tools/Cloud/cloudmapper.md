---
tags: [tool, cloud, aws, visualization]
tool: "cloudmapper"
category: "Cloud"
installed: true
phase: [analysis, reporting]
---

# CloudMapper - AWS Visualization

## Tool Overview
Purpose: Visualize AWS environments and find attack paths
Location: /usr/local/bin/cloudmapper

## When to Use
- AWS network visualization
- Security analysis
- Attack path discovery

## How to Use It

Prepare account data:
cloudmapper collect --account my-account

Generate report:
cloudmapper report --account my-account

Start web server:
cloudmapper serve

Access web UI:
http://localhost:8000

## Related Tools
prowler, scoutsuite

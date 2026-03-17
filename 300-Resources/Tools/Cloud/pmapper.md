---
tags: [tool, cloud, aws, iam]
tool: "pmapper"
category: "Cloud"
installed: true
phase: [analysis, privesc]
---

# Principal Mapper - AWS IAM Analysis

## Tool Overview
Purpose: AWS IAM privilege escalation analysis
Location: /home/kali/.local/bin/pmapper

## When to Use
- IAM role analysis
- Privilege escalation path finding
- Permission visualization

## How to Use It

Generate graph:
pmapper --profile my-account graph

Find privesc paths:
pmapper --profile my-account analysis

Visualize:
pmapper --profile my-account visualize

## Related Tools
pacu, enumerate-iam

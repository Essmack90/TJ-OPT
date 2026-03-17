---
tags: [tool, osint, framework]
tool: "sn0int"
category: "OSINT"
installed: true
phase: [recon]
---

# sn0int - Semi-Automatic OSINT Framework

## Tool Overview
Purpose: OSINT framework with automation capabilities
Location: /usr/bin/sn0int

## When to Use
- Automated OSINT workflows
- Data correlation
- Advanced investigations

## How to Use It

Create Workspace:
sn0int workspace add osint_workspace
sn0int workspace select osint_workspace

List Modules:
sn0int modules list

Run Module:
sn0int run recon/domains-hosts/builtwith -d example.com

Interactive Mode:
sn0int

## Related Tools
recon-ng, spiderfoot

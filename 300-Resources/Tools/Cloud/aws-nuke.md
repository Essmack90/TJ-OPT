---
tags: [tool, cloud, aws, cleanup]
tool: "aws-nuke"
category: "Cloud"
installed: true
phase: [cleanup]
---

# aws-nuke - Delete All AWS Resources

## Tool Overview
Purpose: Remove all resources from an AWS account
Location: /usr/local/bin/aws-nuke

## When to Use
- Account cleanup after testing
- Resource termination
- AWS account reset

## How to Use It

Dry run first:
aws-nuke -c config.yml --dry-run

Execute deletion:
aws-nuke -c config.yml

## Warning
⚠️ This tool is destructive - it will DELETE ALL RESOURCES

## Related Tools
aws-cli

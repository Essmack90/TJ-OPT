---
tags: [tool, cloud, gcp, iam]
tool: "gcp-iam-collector"
category: "Cloud"
installed: true
phase: [recon, enumeration]
---

# GCP IAM Collector

## Tool Overview
Purpose: Collect and analyze GCP IAM permissions
Location: ~/tools/cloud/gcp-iam-collector

## When to Use
- IAM permission enumeration
- Privilege analysis
- Security assessment

## How to Use It

Collect IAM data:
python3 collector.py --project PROJECT_ID

## Related Tools
gcloud, gcpwn

---
tags: [tool, cloud, aws, s3]
tool: "s3scanner"
category: "Cloud"
installed: true
phase: [recon, enumeration]
---

# S3Scanner - Find Open S3 Buckets

## Tool Overview
Purpose: Find and enumerate open S3 buckets
Location: /home/kali/.local/bin/s3scanner

## When to Use
- Finding exposed S3 buckets
- Bucket enumeration
- Data leak discovery

## How to Use It

Scan bucket list:
s3scanner --bucket-file buckets.txt

Check single bucket:
s3scanner --bucket-name target-bucket

## Related Tools
aws-cli, cloudsploit

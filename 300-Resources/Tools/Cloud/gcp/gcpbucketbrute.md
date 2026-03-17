---
tags: [tool, cloud, gcp, buckets]
tool: "gcpbucketbrute"
category: "Cloud"
installed: true
phase: [recon]
---

# GCPBucketBrute - Google Storage Bucket Enumeration

## Tool Overview
Purpose: Enumerate Google Cloud Storage buckets
Location: /home/kali/.local/bin/gcpbucketbrute

## When to Use
- Finding open GCP buckets
- Data leak discovery
- Bucket enumeration

## How to Use It

Brute force bucket names:
gcpbucketbrute -k keyword -w wordlist.txt

Check permissions:
gcpbucketbrute -b bucket-name

## Related Tools
gcloud, gcpwn

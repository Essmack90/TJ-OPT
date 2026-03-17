---
tags: [tool, cloud, gcp]
tool: "gcloud"
category: "Cloud"
installed: true
phase: [recon, exploitation]
---

# gcloud - Google Cloud CLI

## Tool Overview
Purpose: Official CLI for managing Google Cloud Platform
Location: /usr/bin/gcloud

## When to Use
- GCP environment enumeration
- Resource management
- Cloud exploitation

## How to Use It

Login to GCP:
gcloud auth login

List projects:
gcloud projects list

List compute instances:
gcloud compute instances list

List storage buckets:
gsutil ls

## Related Tools
gcpwn, GCPBucketBrute, gcp-iam-collector

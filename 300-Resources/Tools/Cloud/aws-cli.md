---
tags: [tool, cloud, aws]
tool: "aws-cli"
category: "Cloud"
installed: true
phase: [recon, exploitation]
---

# AWS CLI - Amazon Web Services Command Line Interface

## Tool Overview
Purpose: Official CLI for managing AWS services
Location: /usr/bin/aws

## When to Use
- AWS environment enumeration
- Resource management
- Cloud exploitation

## How to Use It

Configure credentials:
aws configure

List S3 buckets:
aws s3 ls

Enumerate IAM users:
aws iam list-users

Describe EC2 instances:
aws ec2 describe-instances

## Related Tools
pacu, enumerate-iam, s3scanner

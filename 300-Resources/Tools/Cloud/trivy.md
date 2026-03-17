---
tags: [tool, cloud, container, security]
tool: "trivy"
category: "Cloud"
installed: true
phase: [scan, security]
---

# Trivy - Container and Cloud Scanner

## Tool Overview
Purpose: Vulnerability scanner for containers and cloud
Location: /usr/bin/trivy

## When to Use
- Container image scanning
- Filesystem vulnerability scanning
- Kubernetes security scanning
- Cloud misconfiguration detection

## How to Use It

Scan container image:
trivy image nginx:latest

Scan filesystem:
trivy fs .

Scan config files:
trivy config ./terraform

## Related Tools
kube-hunter, kube-bench

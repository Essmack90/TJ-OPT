---
tags: [tool, cloud, kubernetes, security]
tool: "kubescape"
category: "Cloud"
installed: true
phase: [scan, security]
---

# Kubescape - Kubernetes Security Scanner

## Tool Overview
Purpose: Comprehensive Kubernetes security scanning
Location: /usr/local/bin/kubescape

## When to Use
- Kubernetes cluster security assessment
- Compliance checking (NSA, MITRE)
- Misconfiguration detection

## How to Use It

Scan cluster:
kubescape scan --submit nsa

Scan manifest files:
kubescape scan manifest.yaml

Generate report:
kubescape scan --format json

## Related Tools
kube-hunter, kube-bench

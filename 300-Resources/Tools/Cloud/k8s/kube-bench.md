---
tags: [tool, cloud, kubernetes, compliance]
tool: "kube-bench"
category: "Cloud"
installed: true
phase: [audit, security]
---

# kube-bench - CIS Benchmark for Kubernetes

## Tool Overview
Purpose: Check Kubernetes against CIS benchmarks
Location: /usr/local/bin/kube-bench

## When to Use
- Kubernetes compliance auditing
- Security configuration checking
- CIS benchmark validation

## How to Use It

Run benchmark:
kube-bench

Run specific test:
kube-bench --check 1.2.3

Output JSON:
kube-bench --json

## Related Tools
kube-hunter, kubescape

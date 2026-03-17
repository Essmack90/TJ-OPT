---
tags: [tool, cloud, kubernetes, security]
tool: "kube-hunter"
category: "Cloud"
installed: true
phase: [scan, security]
---

# kube-hunter - Kubernetes Penetration Testing

## Tool Overview
Purpose: Hunt for security weaknesses in Kubernetes
Location: /home/kali/.local/bin/kube-hunter

## When to Use
- Kubernetes cluster security assessment
- Finding vulnerabilities
- Configuration checks

## How to Use It

Scan remote cluster:
kube-hunter --remote target.com

Scan local cluster:
kube-hunter --local

Interactive mode:
kube-hunter --interface

## Related Tools
kube-bench, kubescape

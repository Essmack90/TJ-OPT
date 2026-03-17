---
tags: [tool, kubernetes, pentesting, recon]
tool: "kubestalk"
category: "Kubernetes"
installed: true
phase: [recon, discovery]
---

# KubeStalk - Kubernetes Attack Surface Discovery

## Tool Overview
Purpose: Black-box discovery of unsecured Kubernetes clusters
Location: ~/tools/cloud/k8s/kubestalk/kubestalk.py

## When to Use
- External reconnaissance for Kubernetes clusters
- Finding exposed Kubelet APIs (port 10250)
- Discovering unauthenticated endpoints
- Initial footprinting of Kubernetes infrastructure

## Why This Tool
**Strengths:**
- Probes for unsecured clusters without credentials
- Detects exposed Kubelet API endpoints
- Identifies dashboard exposures
- Finds etcd misconfigurations

## How to Use It

### Basic Scan
python3 kubestalk.py https://target:10250

### Concurrent Scanning
python3 kubestalk.py https://target --concurrency 10 -o results.csv

### Help
python3 kubestalk.py --help

## What It Detects
- Kubelet API exposure
- Dashboard service exposure
- etcd endpoint exposure
- API server misconfigurations

## Related Tools
kube-hunter, peirates, kubestroyer

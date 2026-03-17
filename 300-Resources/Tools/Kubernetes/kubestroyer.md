---
tags: [tool, kubernetes, exploitation, rce]
tool: "kubestroyer"
category: "Kubernetes"
installed: true
phase: [exploitation, privesc]
---

# Kubestroyer - Kubernetes Exploitation Tool

## Tool Overview
Purpose: Exploit misconfigured Kubernetes clusters
Location: ~/go/bin/Kubestroyer

## When to Use
- Gaining foothold via Kubelet API
- Anonymous command execution
- etcd data extraction
- Node port scanning

## Why This Tool
**Strengths:**
- Scans Kubernetes node ports (30000-32767)
- Anonymous RCE via Kubelet API
- etcd anonymous read access
- Single binary with no dependencies

## How to Use It

### Node Port Scanning
kubestroyer -t localhost --node-scan

### Anonymous RCE via Kubelet
kubestroyer -t localhost --anon-rce -x "ls -al"

### etcd Anonymous Access
kubestroyer -t localhost --etcd

### Help
kubestroyer --help

## Related Tools
peirates, kube-hunter, kubestalk

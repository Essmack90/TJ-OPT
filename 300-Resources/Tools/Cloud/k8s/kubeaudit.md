---
tags: [tool, cloud, kubernetes, audit]
tool: "kubeaudit"
category: "Cloud"
installed: true
phase: [audit, security]
---

# kubeaudit - Kubernetes Security Audit

## Tool Overview
Purpose: Audit Kubernetes clusters for security issues
Location: /usr/local/bin/kubeaudit

## When to Use
- Kubernetes security auditing
- Privilege escalation checks
- Configuration validation

## How to Use It

Audit current context:
kubeaudit all

Audit manifest:
kubeaudit all -f manifest.yaml

## Related Tools
kube-bench, kubescape

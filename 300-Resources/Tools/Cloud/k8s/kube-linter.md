---
tags: [tool, cloud, kubernetes, linting]
tool: "kube-linter"
category: "Cloud"
installed: true
phase: [analysis, security]
---

# kube-linter - Kubernetes YAML Linter

## Tool Overview
Purpose: Lint Kubernetes YAML files for security issues
Location: /usr/local/bin/kube-linter

## When to Use
- YAML validation
- Security best practices
- Misconfiguration detection

## How to Use It

Lint files:
kube-linter lint manifest.yaml

Lint directory:
kube-linter lint manifests/

## Related Tools
kube-score, polaris

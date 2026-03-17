---
tags: [tool, cloud, kubernetes, analysis]
tool: "kube-score"
category: "Cloud"
installed: true
phase: [analysis, security]
---

# kube-score - Kubernetes Object Analysis

## Tool Overview
Purpose: Static code analysis for Kubernetes objects
Location: /usr/local/bin/kube-score

## When to Use
- YAML manifest validation
- Best practice checking
- Security configuration review

## How to Use It

Score manifest files:
kube-score score manifest.yaml

Score directory:
kube-score score manifests/

## Related Tools
kube-linter, polaris

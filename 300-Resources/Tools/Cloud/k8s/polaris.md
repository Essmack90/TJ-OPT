---
tags: [tool, cloud, kubernetes, validation]
tool: "polaris"
category: "Cloud"
installed: true
phase: [analysis, security]
---

# Polaris - Kubernetes Configuration Validator

## Tool Overview
Purpose: Validate Kubernetes configurations against best practices
Location: /usr/local/bin/polaris

## When to Use
- Kubernetes manifest validation
- Best practice checking
- Security configuration review

## How to Use It

Scan cluster:
polaris dashboard --port 8080

Scan manifest files:
polaris audit --audit-path manifests/

## Related Tools
kube-score, kube-linter

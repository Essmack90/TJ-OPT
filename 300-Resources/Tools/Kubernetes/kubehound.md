---
tags: [tool, kubernetes, analysis, attack-path]
tool: "kubehound"
category: "Kubernetes"
installed: true
phase: [analysis, privesc]
---

# KubeHound - Kubernetes Attack Path Discovery

## Tool Overview
Purpose: Identify multi-step attack paths through Kubernetes clusters
Location: ~/go/bin/kubehound

## When to Use
- Post-compromise path analysis
- Privilege escalation discovery
- RBAC misconfiguration analysis
- Attack surface visualization

## Why This Tool
- Maps attack paths like BloodHound for AD
- Identifies privilege escalation chains
- Analyzes RBAC permissions
- Finds multi-step attack vectors

## How to Use It

Basic Scan:
kubehound --config config.yaml

Generate Report:
kubehound --config config.yaml --output report

Help:
kubehound --help

## Configuration Example

Create a config.yaml file with:
cluster:
  name: my-cluster
  context: my-context
collectors:
  - rbac
  - pods
  - services

## Related Tools
peirates, kubestroyer, bloodhound

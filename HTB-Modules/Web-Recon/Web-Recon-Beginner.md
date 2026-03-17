---
tags: [module/web-recon, reconnaissance, active, passive, level/beginner]
---

# Information Gathering - Web Edition - Beginner's Guide

## What is Web Reconnaissance?

Web reconnaissance is the process of gathering information about a target website or web application BEFORE you start testing it. Think of it like a detective gathering clues before solving a case.

It's the foundation of EVERY penetration test. Skip it, and you'll miss things.

---

## Why Do We Need Web Recon?

| Goal | Why It Matters |
|------|----------------|
| Find all assets | You can't test what you don't know exists |
| Discover hidden stuff | Backup files, config files, internal docs get left exposed |
| Map the attack surface | Understand what you're dealing with |
| Gather intel | Find employees, emails, patterns for social engineering |

**The Rule:** The more you know about the target, the easier the test becomes.

---

## Two Types of Reconnaissance

### Active Reconnaissance

You directly interact with the target. Like knocking on doors to see which ones open.

| Technique | What It Does | Example | Risk |
|-----------|--------------|---------|------|
| Port Scanning | Finds open ports | Nmap scanning for port 80, 443 | HIGH - You're touching the target |
| Vuln Scanning | Probes for weaknesses | Nessus checking for SQLi | HIGH - Sends exploit payloads |
| Banner Grabbing | Reads service banners | `nc target.com 80` and see what replies | LOW - Just asking politely |
| OS Fingerprinting | Identifies the OS | Nmap `-O` flag | LOW - Passive analysis |
| Service Enumeration | Gets version numbers | Nmap `-sV` flag | LOW - Version detection |
| Web Spidering | Crawls the website | Burp Spider mapping pages | LOW/MED - Can be noisy |

**The Problem:** Active recon can get you caught. Firewalls, IDS, and logging will see you.

### Passive Reconnaissance

You NEVER touch the target. You just look at public information. Like reading newspapers about a building instead of walking around it.

| Technique | What It Does | Example | Risk |
|-----------|--------------|---------|------|
| Search Engines | Google the target | "target.com employees" | NONE - Normal internet use |
| WHOIS | Look up domain registration | `whois target.com` | NONE - Public records |
| DNS | Check DNS records | `dig target.com ANY` | NONE - Normal DNS queries |
| Wayback Machine | See old versions of site | archive.org | NONE - Public archive |
| Social Media | Check LinkedIn/Twitter | Search for employees | NONE - Public profiles |
| GitHub | Search for leaked code | Search target name in code | NONE - Public repos |

**The Advantage:** Nobody knows you're looking. No logs, no alerts, no blocks.

---

## Key Takeaways

- Recon is the MOST important phase of any pentest
- Active recon = direct interaction (risky but detailed)
- Passive recon = no interaction (safe but limited)
- Always start passive, then move to active
- Document EVERYTHING you find
- You can't exploit what you don't know exists
- The quieter you are, the longer you'll have access

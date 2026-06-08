---
tags: [module/web-recon, whois, passive-recon, osint, level/beginner]
---

# Utilizing WHOIS - Beginner's Guide

## What Can WHOIS Tell You?

WHOIS data helps you understand who owns a domain, when it was registered, and how it's configured. This information is valuable for investigations, threat intelligence, and penetration testing.

---

## Three Real-World Scenarios

### Scenario 1: Phishing Investigation

An employee receives a suspicious email claiming to be from their bank. A security analyst performs a WHOIS lookup on the linked domain.

What the analyst finds:
- Domain registered 3 days ago
- Registrant info hidden by privacy service
- Name servers from a known bulletproof hosting provider

Conclusion: Clear signs of a phishing campaign. The domain is blocked and employees are warned.

### Scenario 2: Malware Analysis

A researcher analyzes malware that communicates with a remote command-and-control (C2) server.

What the researcher finds:
- Domain registered to an individual using a free, anonymous email service
- Registrant address in a country with high cybercrime activity
- Registrar known for lax abuse policies

Conclusion: The C2 server is likely bulletproof hosting. The researcher notifies the hosting provider.

### Scenario 3: Threat Intelligence Report

A cybersecurity firm tracks a sophisticated threat actor group targeting financial institutions.

What analysts find across multiple domains:
- Domains registered in clusters right before attacks
- Various aliases and fake identities used
- Same name servers across multiple domains (shared infrastructure)
- Many domains taken down after attacks

Conclusion: They build a profile of the attacker's TTPs and create IOCs for other organizations to use.

---

## Installing WHOIS

Before using WHOIS, install it on your system:

sudo apt update
sudo apt install whois -y

---

## Basic WHOIS Lookup

### Example: facebook.com

whois facebook.com

### Key Information Revealed

Domain Name: FACEBOOK.COM
Creation Date: 1997-03-29
Registry Expiry Date: 2033-03-30
Registrar: RegistrarSafe, LLC
Registrant Organization: Meta Platforms, Inc.
Registrant Name: Domain Admin
Name Server: A.NS.FACEBOOK.COM
Name Server: B.NS.FACEBOOK.COM
Name Server: C.NS.FACEBOOK.COM
Name Server: D.NS.FACEBOOK.COM

---

## What Each Field Means

| Field | What It Tells You |
|-------|-------------------|
| Creation Date | How long the domain has existed (old = established, new = suspicious) |
| Expiry Date | When registration lapses (lapses = opportunity) |
| Registrar | Where it was registered (some registrars are more lax than others) |
| Registrant Organization | The company that owns it |
| Registrant Name | Contact person (often generic like Domain Admin) |
| Name Servers | DNS infrastructure (custom name servers = large org) |
| Domain Status | Security protections (clientDeleteProhibited = protected) |

---

## Domain Status Codes Explained

| Status | Meaning |
|--------|---------|
| clientDeleteProhibited | Domain cannot be deleted |
| clientTransferProhibited | Domain cannot be transferred to another registrar |
| clientUpdateProhibited | Domain details cannot be updated |
| serverDeleteProhibited | Registry-level protection against deletion |
| serverTransferProhibited | Registry-level protection against transfer |
| serverUpdateProhibited | Registry-level protection against updates |

These statuses indicate the domain owner takes security seriously.

---

## Red Flags in WHOIS Data

| Red Flag | What It Suggests |
|----------|-------------------|
| Recently registered | Possible phishing or malicious site |
| Privacy protection | Owner hiding identity (sometimes legitimate, sometimes not) |
| Suspicious registrar | Some registrars ignore abuse reports |
| Bulletproof hosting | Hosting provider that ignores abuse complaints |
| Mismatched details | Inconsistent information across records |
| Recently changed | Domain may have changed hands |

---

## Key Takeaways

- WHOIS helps identify domain ownership and infrastructure
- Recent registration + hidden details + suspicious hosting = likely malicious
- Large organizations like Meta use custom name servers and domain protections
- Domain status codes show security measures
- Always check WHOIS during investigations
- Combine WHOIS with other recon techniques for full picture

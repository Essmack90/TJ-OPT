---
tags: [tool, activedirectory, mitm]
tool: "responder"
category: "Active Directory"
installed: true
phase: [post-exploit, credential]
---

# Responder - LLMNR/NBT-NS/mDNS Poisoner

## Tool Overview
Purpose: Poison name resolution services to capture hashes
Location: /usr/bin/responder

## When to Use
- Windows network attacks
- Capturing NTLM hashes
- SMB relay preparation

## How to Use It

Basic Poisoning:
sudo responder -I eth0

All Services:
sudo responder -I eth0 -rdw

Analyze Mode (no poisoning):
sudo responder -I eth0 -A

## Output Files
Captured hashes in /usr/share/responder/logs/

## Related Tools
ntlmrelayx, impacket

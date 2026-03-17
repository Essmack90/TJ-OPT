---
tags: [tool, privesc, windows, enumeration, smb]
tool: "enum4linux-ng"
category: "Privesc"
installed: true
phase: [recon, enumeration]
---

# enum4linux-ng - Windows/Samba Enumeration Tool

## Tool Overview
Purpose: Enumerate Windows and Samba hosts for users, shares, and system information
Location: /usr/bin/enum4linux-ng

## When to Use
- Initial reconnaissance of Windows targets
- To enumerate SMB shares and users
- When you have SMB access to a target

## How to Use It

Basic Scan:
enum4linux-ng -A target.com

Users Only:
enum4linux-ng -U target.com

Shares Only:
enum4linux-ng -S target.com

All Information:
enum4linux-ng -A -u username -p password target.com

JSON Output:
enum4linux-ng -A target.com -oJ output

Verbose:
enum4linux-ng -A -v target.com

## What It Finds
- Domain and workgroup information
- Users list
- Shares
- Password policy
- OS information
- Groups
- Sessions

## Related Tools
smbclient, ldapdomaindump, smbmap

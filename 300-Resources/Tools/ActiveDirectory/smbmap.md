---
tags: [tool, activedirectory, smb]
tool: "smbmap"
category: "Active Directory"
installed: true
phase: [enumeration, lateral]
---

# smbmap - SMB Share Mapper

## Tool Overview
Purpose: Enumerate SMB shares and permissions
Location: /usr/bin/smbmap

## When to Use
- Finding accessible SMB shares
- Checking share permissions
- Uploading/downloading files

## How to Use It

List Shares:
smbmap -H target.com

With Credentials:
smbmap -u user -p pass -d domain -H target.com

Recursive Share Listing:
smbmap -H target.com -R share

Execute Command:
smbmap -H target.com -u user -p pass -x 'whoami'

## Related Tools
smbclient, enum4linux-ng

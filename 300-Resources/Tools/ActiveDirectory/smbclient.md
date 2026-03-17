---
tags: [tool, activedirectory, smb]
tool: "smbclient"
category: "Active Directory"
installed: true
phase: [enumeration, lateral]
---

# smbclient - SMB Client

## Tool Overview
Purpose: SMB client for Windows shares
Location: /usr/bin/smbclient

## How to Use It

List Shares:
smbclient -L //target.com -N

Connect to Share:
smbclient //target.com/share -U username

With Password:
smbclient //target.com/share -U username%password

## Related Tools
smbmap, enum4linux-ng

---
tags: [tool, smb, windows]
tool: "smbmap"
category: "Network SMB"
installed: true
phase: [recon, lateral]
---

# smbmap - SMB Share Mapper

## Overview
Enumerate SMB shares and permissions

## Location
/usr/bin/smbmap

## Basic Usage
smbmap -H target.com
smbmap -u user -p pass -d domain -H target.com
smbmap -H target.com -R share

## Common Options
-H : Host
-u : Username
-p : Password
-R : Recursive listing

## Related Tools
smbclient, enum4linux

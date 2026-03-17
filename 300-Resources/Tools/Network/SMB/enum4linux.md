---
tags: [tool, smb, windows]
tool: "enum4linux"
category: "Network SMB"
installed: true
phase: [recon]
---

# enum4linux - Windows Enumeration

## Overview
Enumerate Windows and Samba systems

## Location
/usr/bin/enum4linux

## Basic Usage
enum4linux -a target.com
enum4linux -U target.com
enum4linux -S target.com

## Common Options
-a : All enumeration
-U : Get users
-S : Get shares
-P : Password policy

## Related Tools
smbclient, enum4linux-ng

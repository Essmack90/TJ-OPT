---
tags: [tool, smb, windows]
tool: "enum4linux-ng"
category: "Network SMB"
installed: true
phase: [recon]
---

# enum4linux-ng - Next Gen Enumeration

## Overview
Modern rewrite of enum4linux

## Location
/usr/bin/enum4linux-ng

## Basic Usage
enum4linux-ng -A target.com
enum4linux-ng -U target.com
enum4linux-ng -S target.com

## Common Options
-A : All enumeration
-U : Get users
-S : Get shares
-P : Password policy

## Related Tools
smbclient, enum4linux

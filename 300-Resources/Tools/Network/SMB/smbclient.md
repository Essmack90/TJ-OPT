---
tags: [tool, smb, windows]
tool: "smbclient"
category: "Network SMB"
installed: true
phase: [recon, lateral]
---

# smbclient - SMB Client

## Overview
SMB client for Windows shares

## Location
/usr/bin/smbclient

## Basic Usage
smbclient -L //target.com -N
smbclient //target.com/share -U username

## Common Commands
ls : List files
get : Download file
put : Upload file
exit : Exit session

## Related Tools
enum4linux, smbmap

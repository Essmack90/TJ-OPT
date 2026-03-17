---
tags: [tool, netbios, windows]
tool: "nbtscan"
category: "Network SMB"
installed: true
phase: [recon]
---

# nbtscan - NetBIOS Scanner

## Overview
Scan for NetBIOS name information

## Location
/usr/bin/nbtscan

## Basic Usage
nbtscan 192.168.1.0/24
nbtscan -v 192.168.1.0/24

## Common Options
-v : Verbose output
-l : List format

## Related Tools
enum4linux, smbclient

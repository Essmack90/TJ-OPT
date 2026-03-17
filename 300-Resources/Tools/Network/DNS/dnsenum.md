---
tags: [tool, dns, recon]
tool: "dnsenum"
category: "Network DNS"
installed: true
phase: [recon]
---

# dnsenum - DNS Enumeration

## Overview
Comprehensive DNS enumeration tool

## Location
/usr/bin/dnsenum

## Basic Usage
dnsenum example.com
dnsenum --enum example.com -v
dnsenum -f subdomains.txt example.com

## Common Options
--enum : Full enumeration
-f : Dictionary file
-o : Output file

## Related Tools
dnsrecon, fierce

---
tags: [tool, dns, recon]
tool: "dnsrecon"
category: "Network DNS"
installed: true
phase: [recon]
---

# dnsrecon - DNS Enumeration

## Overview
DNS reconnaissance and enumeration

## Location
/usr/bin/dnsrecon

## Basic Usage
dnsrecon -d example.com
dnsrecon -d example.com -t axfr
dnsrecon -d example.com -D subdomains.txt -t brt

## Common Options
-d : Domain
-t : Scan type
-D : Dictionary file

## Related Tools
dnsenum, fierce

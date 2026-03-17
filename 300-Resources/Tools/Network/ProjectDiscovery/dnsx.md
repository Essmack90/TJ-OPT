---
tags: [tool, dns, probe]
tool: "dnsx"
category: "Network ProjectDiscovery"
installed: true
phase: [recon]
---

# dnsx - DNS Toolkit

## Overview
Fast DNS query tool

## Location
~/go/bin/dnsx

## Basic Usage
echo "example.com" | dnsx
echo "example.com" | dnsx -a -cname

## Common Options
-a : A records
-cname : CNAME records
-aaaa : AAAA records
-txt : TXT records

## Related Tools
dig, dnsrecon

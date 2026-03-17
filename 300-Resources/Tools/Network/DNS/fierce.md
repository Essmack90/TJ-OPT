---
tags: [tool, dns, recon]
tool: "fierce"
category: "Network DNS"
installed: true
phase: [recon]
---

# fierce - DNS Reconnaissance

## Overview
DNS enumeration and subdomain discovery

## Location
/usr/bin/fierce

## Basic Usage
fierce --domain example.com
fierce --domain example.com --wordlist subdomains.txt
fierce --domain example.com --wide

## Common Options
--domain : Target domain
--wordlist : Dictionary file
--wide : Scan entire CIDR

## Related Tools
dnsrecon, dnsenum

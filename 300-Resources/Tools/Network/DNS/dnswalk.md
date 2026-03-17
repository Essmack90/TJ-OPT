---
tags: [tool, dns, recon]
tool: "dnswalk"
category: "Network DNS"
installed: true
phase: [recon]
---

# dnswalk - DNS Zone Walker

## Overview
Check DNS zone for consistency and errors

## Location
/usr/bin/dnswalk

## Basic Usage
dnswalk example.com.
dnswalk -r example.com.

## Common Options
-r : Check reverse records

## Related Tools
dnsrecon, dnsenum

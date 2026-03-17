---
tags: [tool, dns, mitm]
tool: "dnschef"
category: "Network DNS"
installed: true
phase: [mitm]
---

# dnschef - DNS Proxy

## Overview
DNS proxy for spoofing and manipulation

## Location
/usr/bin/dnschef

## Basic Usage
dnschef --fakeip 192.168.1.100
dnschef --fakedomain google.com=192.168.1.100

## Common Options
--fakeip : IP to spoof
--fakedomain : Domain to spoof

## Related Tools
dnsspoof, bettercap

---
tags: [tool, network, mitm]
tool: "dnsspoof"
category: "Network MITM"
installed: true
phase: [post-exploit, mitm]
---

# dnsspoof - DNS Spoofing

## Overview
Spoof DNS replies to redirect traffic

## Location
/usr/sbin/dnsspoof

## Basic Usage
echo "192.168.1.100 google.com" > hosts.txt
sudo dnsspoof -i eth0 -f hosts.txt

## Common Options
-i : Interface
-f : Hosts file

## Related Tools
dsniff, ettercap, bettercap

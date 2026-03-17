---
tags: [tool, network, traceroute]
tool: "traceroute"
category: "Network Performance"
installed: true
phase: [recon]
---

# traceroute - Network Path Discovery

## Overview
Print the route packets take to network host

## Location
/usr/bin/traceroute

## Basic Usage
traceroute google.com
traceroute -n google.com
traceroute -I google.com (ICMP)

## Common Options
-n : No DNS resolution
-I : Use ICMP
-T : Use TCP

## Related Tools
mtr, tcptraceroute
